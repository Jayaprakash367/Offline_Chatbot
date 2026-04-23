"""
Fine-tune a bilingual (Tamil + English) Jarvis conversational model with a
low-memory QLoRA profile suitable for 1B-3B base models.

Example:
    python train_billion_jarvis.py \
        --base-model Qwen/Qwen2.5-1.5B-Instruct \
        --dataset data/training_conversations.sample.jsonl \
        --output-dir models/jarvis-bilingual-1b \
        --epochs 2
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


SYSTEM_PROMPT = (
    "You are JARVIS, a friendly assistant. "
    "Reply naturally in Tamil, English, or mixed Tamil-English based on user language. "
    "Be respectful, empathetic, practical, and concise. "
    "Do not produce harmful content."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune bilingual Jarvis 1B+ model with QLoRA")
    parser.add_argument(
        "--base-model",
        default="Qwen/Qwen2.5-1.5B-Instruct",
        help="Hugging Face base model name (1B-3B recommended for local speed)",
    )
    parser.add_argument(
        "--dataset",
        default="data/training_conversations.sample.jsonl",
        help="Path to JSONL dataset with {user, assistant, language?, emotion?}",
    )
    parser.add_argument(
        "--output-dir",
        default="models/jarvis-bilingual-1b",
        help="Folder to save LoRA adapter and tokenizer",
    )
    parser.add_argument("--max-seq-len", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--max-steps", type=int, default=-1, help="Overrides epochs when > 0")
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--warmup-ratio", type=float, default=0.05)
    parser.add_argument("--save-steps", type=int, default=120)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit loading")

    parser.add_argument("--lora-r", type=int, default=32)
    parser.add_argument("--lora-alpha", type=int, default=64)
    parser.add_argument("--lora-dropout", type=float, default=0.05)

    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as ex:
                raise ValueError(f"Invalid JSON on line {line_no}: {ex}") from ex

            user_text = str(item.get("user", "")).strip()
            assistant_text = str(item.get("assistant", "")).strip()
            if not user_text or not assistant_text:
                continue

            rows.append(
                {
                    "user": user_text,
                    "assistant": assistant_text,
                    "language": str(item.get("language", "auto")).strip().lower() or "auto",
                    "emotion": str(item.get("emotion", "neutral")).strip().lower() or "neutral",
                }
            )

    if not rows:
        raise ValueError("Dataset has no valid training rows")

    return rows


def format_example(row: dict) -> str:
    language = row.get("language", "auto")
    emotion = row.get("emotion", "neutral")

    return (
        f"### SYSTEM\n{SYSTEM_PROMPT}\n"
        f"Language hint: {language}\n"
        f"User emotion hint: {emotion}\n\n"
        f"### USER\n{row['user']}\n\n"
        f"### ASSISTANT\n{row['assistant']}"
    )


def build_dataset(rows: list[dict], seed: int) -> Dataset:
    random.Random(seed).shuffle(rows)
    texts = [format_example(row) for row in rows]
    return Dataset.from_dict({"text": texts})


def build_model_and_tokenizer(
    base_model: str,
    use_4bit: bool,
) -> tuple[AutoModelForCausalLM, AutoTokenizer, bool]:
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    cuda_available = torch.cuda.is_available()
    use_4bit_runtime = bool(use_4bit and cuda_available)

    if use_4bit_runtime:
        compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=compute_dtype,
        )

        try:
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                quantization_config=quant_config,
                device_map="auto",
                trust_remote_code=True,
            )
            model = prepare_model_for_kbit_training(model)
            return model, tokenizer, True
        except Exception as ex:
            print(f"[WARN] 4-bit loading failed ({ex}). Falling back to full precision mode.")

    dtype = torch.bfloat16 if cuda_available and torch.cuda.is_bf16_supported() else (
        torch.float16 if cuda_available else torch.float32
    )

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map="auto" if cuda_available else None,
        trust_remote_code=True,
    )
    return model, tokenizer, False


def tokenize_dataset(dataset: Dataset, tokenizer: AutoTokenizer, max_seq_len: int) -> Dataset:
    def tokenize_batch(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_seq_len,
        )

    return dataset.map(
        tokenize_batch,
        batched=True,
        remove_columns=["text"],
        desc="Tokenizing dataset",
    )


def apply_lora(model: AutoModelForCausalLM, args: argparse.Namespace) -> AutoModelForCausalLM:
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def save_runtime_hint(output_dir: Path, base_model: str, used_4bit: bool) -> None:
    hint = {
        "base_model": base_model,
        "training_profile": "qlora" if used_4bit else "lora",
        "note": (
            "Use this adapter for local inference. For Jarvis runtime with Ollama, "
            "export/convert your trained model and set JARVIS_BILLION_MODEL + JARVIS_USE_BILLION_MODEL=1."
        ),
        "env_example": {
            "JARVIS_USE_BILLION_MODEL": "1",
            "JARVIS_BILLION_MODEL": "your-finetuned-model-name",
            "JARVIS_SPEED_PROFILE": "balanced",
        },
    }

    hint_path = output_dir / "runtime_hint.json"
    with hint_path.open("w", encoding="utf-8") as f:
        json.dump(hint, f, indent=2, ensure_ascii=False)


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)

    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Loading dataset: {dataset_path}")
    rows = load_jsonl(dataset_path)
    print(f"[INFO] Loaded {len(rows)} conversation rows")

    train_dataset = build_dataset(rows, seed=args.seed)

    print(f"[INFO] Loading base model: {args.base_model}")
    model, tokenizer, used_4bit = build_model_and_tokenizer(
        base_model=args.base_model,
        use_4bit=not args.no_4bit,
    )

    model = apply_lora(model, args)
    tokenized_dataset = tokenize_dataset(train_dataset, tokenizer, args.max_seq_len)

    fp16 = torch.cuda.is_available() and not torch.cuda.is_bf16_supported()
    bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()

    optim_name = "paged_adamw_8bit" if used_4bit else "adamw_torch"

    train_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        warmup_ratio=args.warmup_ratio,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=2,
        fp16=fp16,
        bf16=bf16,
        optim=optim_name,
        lr_scheduler_type="cosine",
        gradient_checkpointing=True,
        dataloader_pin_memory=torch.cuda.is_available(),
        report_to="none",
    )

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=tokenized_dataset,
        data_collator=collator,
        tokenizer=tokenizer,
    )

    print("[INFO] Starting training")
    trainer.train()

    print(f"[INFO] Saving adapter to: {output_dir}")
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    save_runtime_hint(output_dir, args.base_model, used_4bit)

    print("[INFO] Training finished successfully")


if __name__ == "__main__":
    main()
