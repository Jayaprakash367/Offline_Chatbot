"""
=============================================================
  MODULE 7 — KNOWLEDGE BASE (Offline Q&A)
  Retrieval-based question answering from local JSON.
  Uses fuzzy string matching — no ML, no internet.
  Never guesses; admits when it doesn't know.
=============================================================
"""

import json
import re
from difflib import SequenceMatcher
from typing import Optional, Tuple

from config import KNOWLEDGE_BASE_FILE


class KnowledgeBase:
    """Answers user questions from a locally stored knowledge base."""

    def __init__(self):
        self.entries: list = []
        self._load()

    # ── public API ────────────────────────────────────────

    def search(self, query: str) -> Tuple[Optional[str], float]:
        """
        Search the knowledge base for an answer.

        Returns
        -------
        (answer_text, confidence)
        If nothing matches, returns (None, 0.0).
        """
        if not query or not self.entries:
            return (None, 0.0)

        query_clean = self._normalise(query)
        best_answer = None
        best_score = 0.0

        for entry in self.entries:
            question = self._normalise(entry.get("question", ""))
            score = self._similarity(query_clean, question)

            if score > best_score:
                best_score = score
                best_answer = entry.get("answer", "")

        if best_score < 0.50:
            return (None, best_score)

        return (best_answer, round(best_score, 3))

    def add_entry(self, question: str, answer: str) -> bool:
        """Add a new Q&A pair to the knowledge base and persist."""
        if not question or not answer:
            return False

        # Check for duplicate
        q_norm = self._normalise(question)
        for entry in self.entries:
            if self._similarity(q_norm, self._normalise(entry["question"])) > 0.85:
                # Update existing
                entry["answer"] = answer
                self._save()
                return True

        self.entries.append({"question": question.strip(), "answer": answer.strip()})
        self._save()
        return True

    def reload(self) -> None:
        self._load()

    # ── private helpers ───────────────────────────────────

    def _load(self) -> None:
        try:
            with open(KNOWLEDGE_BASE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.entries = data.get("entries", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[KnowledgeBase] Warning: {e}")
            self.entries = []

    def _save(self) -> None:
        try:
            with open(KNOWLEDGE_BASE_FILE, "w", encoding="utf-8") as f:
                json.dump({"entries": self.entries}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[KnowledgeBase] Save error: {e}")

    @staticmethod
    def _normalise(text: str) -> str:
        """Lowercase, strip punctuation, collapse whitespace."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """Combined similarity: SequenceMatcher + word overlap."""
        if not a or not b:
            return 0.0

        # Sequence similarity
        seq_score = SequenceMatcher(None, a, b).ratio()

        # Word-overlap (Jaccard-like)
        words_a = set(a.split())
        words_b = set(b.split())
        union = words_a | words_b
        if union:
            jaccard = len(words_a & words_b) / len(union)
        else:
            jaccard = 0.0

        # Weighted blend
        return 0.6 * seq_score + 0.4 * jaccard
