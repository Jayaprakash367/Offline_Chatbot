# OfflineAI — Fully Offline, Secure, Emotion-Aware Windows AI Assistant

## Complete Architecture Documentation & Viva Guide

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Module-by-Module Breakdown](#3-module-by-module-breakdown)
4. [Data Flow](#4-data-flow)
5. [Dual-Mode Intelligence](#5-dual-mode-intelligence)
6. [Security Architecture](#6-security-architecture)
7. [Training Data Format](#7-training-data-format)
8. [Installation & Setup](#8-installation--setup)
9. [JARVIS Visual App (Desktop + Web + Hybrid Models)](#9-jarvis-visual-app-desktop--web--hybrid-models)
10. [Building the Executable](#10-building-the-executable)
11. [Viva Q&A — Key Explanations](#11-viva-qa--key-explanations)
12. [Ethics & Limitations](#12-ethics--limitations)
13. [Future Enhancements](#13-future-enhancements)

---

## 1. System Overview

**OfflineAI** is a personal, friendly, emotion-aware AI assistant that runs entirely on a Windows PC with **zero internet connectivity**. It is designed as a final-year engineering project that a single student can build, understand, and defend in a viva.

### Key Properties

| Property | Description |
|---|---|
| **Fully Offline** | No internet, no cloud APIs, no external datasets |
| **Voice + Text** | Speaks and listens using Windows-native engines |
| **Emotion-Aware** | Detects sad, stressed, angry, happy, neutral |
| **Command Executor** | Opens/closes apps, checks system health |
| **Knowledge Base** | Answers questions from local JSON data |
| **Learnable** | Users can teach it new Q&A pairs |
| **Secure** | Whitelist-only commands, input validation, no admin |
| **Portable** | Packages into a `.exe` — no Python required |

---

## 2. Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                      USER                                │
│              (Voice or Keyboard Input)                   │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────┐
│   MODULE 1: VOICE INPUT  │  ← Offline Speech Recognition
│   (SpeechRecognition +   │    (PocketSphinx / Vosk)
│    PocketSphinx)         │
└──────────┬───────────────┘
           │ raw text
           ▼
┌──────────────────────────┐
│   SECURITY GATE          │  ← Input validation
│   (Length, blocked words) │    Rejects unsafe input
└──────────┬───────────────┘
           │ validated text
           ▼
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐  ┌────────────┐
│INTENT  │  │  EMOTION   │    ← PARALLEL analysis
│DETECTOR│  │  DETECTOR  │
│(Mod 2) │  │  (Mod 3)   │
└───┬────┘  └─────┬──────┘
    │             │
    ▼             ▼
┌──────────────────────────┐
│   MODULE 4: DECISION     │  ← The "Brain"
│        ENGINE            │
│                          │
│  IF command → execute    │
│  IF emotion → comfort    │
│  IF both    → do BOTH    │
│  IF unknown → KB search  │
└──┬──────┬──────┬─────────┘
   │      │      │
   ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌──────────┐
│CMD  │ │RESP │ │KNOWLEDGE │
│EXEC │ │ENG  │ │  BASE    │
│(M5) │ │(M6) │ │  (M7)    │
└─────┘ └──┬──┘ └──────────┘
           │
           ▼
┌──────────────────────────┐
│  MODULE 8: MEMORY        │  ← Saves history, prefs
│  (Local JSON)            │
└──────────────────────────┘
           │
           ▼
┌──────────────────────────┐
│  MODULE 9: VOICE OUTPUT  │  ← Offline TTS (pyttsx3)
│  (Windows SAPI5)         │
└──────────────────────────┘
           │
           ▼
┌──────────────────────────┐
│        USER              │
│   (Hears spoken response │
│    + sees text output)   │
└──────────────────────────┘
```

---

## 3. Module-by-Module Breakdown

### Module 1 — Voice Input (`voice_input.py`)

**Purpose:** Capture user speech and convert to text offline.

| Aspect | Detail |
|---|---|
| Library | `SpeechRecognition` + `PocketSphinx` |
| Fallback | Text input if no microphone |
| Privacy | Audio is **never recorded or stored** |
| How it works | Adjusts for ambient noise → listens → sends audio to PocketSphinx offline engine → returns text |

### Module 2 — Intent Detector (`intent_detector.py`)

**Purpose:** Classify what the user *wants to do*.

| Aspect | Detail |
|---|---|
| Method | Pattern matching with `{entity}` placeholders + fuzzy matching (SequenceMatcher) |
| Data | `intent_data.json` — locally created patterns |
| Output | `(intent_tag, confidence, entities)` e.g. `("open_app", 0.92, {"app": "notepad"})` |
| No ML needed | Simple string matching + word overlap scoring achieves >85% accuracy on expected inputs |

### Module 3 — Emotion Detector (`emotion_detector.py`)

**Purpose:** Detect how the user is *feeling*.

| Aspect | Detail |
|---|---|
| Method | Keyword scoring + phrase matching + intensifier boosting + negation handling |
| Emotions | Sad, Stressed, Angry, Happy, Neutral |
| Data | `emotion_data.json` with keywords, phrases, weights |
| Intelligence | "not happy" correctly reduces happy score via negation detection |

### Module 4 — Decision Engine (`decision_engine.py`)

**Purpose:** The central "brain" — orchestrates everything.

| Step | Action |
|---|---|
| 1 | **Security Gate** — validate input |
| 2 | **Parallel Analysis** — detect intent AND emotion simultaneously |
| 3 | **Dual-Mode Decision** — command? emotion? both? |
| 4 | **Route** to appropriate handler |
| 5 | **Persist** to memory |

### Module 5 — Command Executor (`command_executor.py`)

**Purpose:** Execute safe, whitelisted system commands.

| Aspect | Detail |
|---|---|
| Open apps | `subprocess.Popen()` for whitelisted apps only |
| Close apps | `taskkill /IM` (no force) for approved processes |
| System status | `psutil` for CPU / RAM / battery |
| Safety | Double validation: whitelist check + blocked keyword check |

### Module 6 — Response Engine (`response_engine.py`)

**Purpose:** Generate friendly, human-like responses.

| Aspect | Detail |
|---|---|
| Templates | Multiple responses per category in `responses.json` |
| Randomization | Picks randomly for variety |
| Personalization | Supports `{app}`, `{time}`, `{date}`, `{name}` placeholders |
| Emotion | Separate empathetic response templates per emotion |

### Module 7 — Knowledge Base (`knowledge_base.py`)

**Purpose:** Offline Q&A from local data.

| Aspect | Detail |
|---|---|
| Storage | `knowledge_base.json` with Q&A pairs |
| Search | Combined SequenceMatcher + Jaccard similarity |
| Teachable | Users can add new Q&A pairs that persist |
| Honesty | Returns "I don't know" if confidence < 50% |

### Module 8 — Memory (`memory.py`)

**Purpose:** Remember user across sessions.

| Stored | Purpose |
|---|---|
| `user_name` | Personalized greetings |
| `conversation_count` | Track usage |
| `conversation_history` | Context (last 50 turns) |
| `learned_facts` | User-taught knowledge |
| `preferences` | User settings |

### Module 9 — Voice Output (`voice_output.py`)

**Purpose:** Speak responses aloud.

| Aspect | Detail |
|---|---|
| Engine | `pyttsx3` wrapping Windows SAPI5 |
| Voices | Microsoft Zira (female) / David (male) |
| Offline | 100% — uses built-in Windows speech engine |
| Configurable | Speed, volume, voice selection |

---

## 4. Data Flow

```
User speaks → Mic captures audio → PocketSphinx converts to text
           → Security validates text
           → Intent Detector classifies (what to do?)
           → Emotion Detector classifies (how are they feeling?)
           → Decision Engine decides:
               ├── Command only → Execute + respond
               ├── Emotion only → Comfort response
               ├── Both → Execute command + comfort
               └── Unknown → Search Knowledge Base
           → Response Engine formats reply
           → Memory saves turn
           → Voice Output speaks response
```

### Safety Checkpoints in the Flow

1. **Input Validation** — text length limit, blocked keywords
2. **Whitelist Check** — only approved apps can be opened/closed
3. **No Admin** — runs as standard user, no elevated privileges
4. **No File Access** — cannot read, write, or delete user files
5. **No Network** — no outbound connections possible

---

## 5. Dual-Mode Intelligence

This is the **most important design feature**. The system handles three scenarios:

### Scenario 1: Command Only
```
User: "Open Notepad"
→ Intent: open_app (confidence: 0.95, entity: notepad)
→ Emotion: neutral
→ Action: Opens Notepad
→ Response: "Opening Notepad for you right now!"
```

### Scenario 2: Emotion Only
```
User: "I'm feeling really stressed today"
→ Intent: unknown
→ Emotion: stressed (confidence: 0.85)
→ Action: No command
→ Response: "It sounds like you're under a lot of pressure. Take a deep breath..."
```

### Scenario 3: BOTH (Dual Mode)
```
User: "Open VS Code... I'm stressed"
→ Intent: open_app (entity: vs code)
→ Emotion: stressed
→ Action: Opens VS Code + empathetic response
→ Response: "Opening VS Code for you!
             Also — It sounds like you're under pressure..."
```

---

## 6. Security Architecture

### Threat Model

| Threat | Mitigation |
|---|---|
| Arbitrary command execution | Whitelist-only approach |
| File deletion / damage | No file operations permitted |
| Data exfiltration | No network access, no internet libraries |
| Privilege escalation | Runs as standard user |
| Input injection | Length limits + blocked keywords |
| Background spying | No persistent listeners; mic only active during listen() |
| Password theft | No access to credential stores |
| Dependency attacks | All packages are stable, audited, offline-capable |

### Security Layers

```
Layer 1: INPUT VALIDATION
  └── Max 500 chars, blocked keyword filter

Layer 2: INTENT WHITELIST
  └── Only known intent tags are processed

Layer 3: COMMAND WHITELIST
  └── Only pre-approved apps can be opened/closed

Layer 4: OS-LEVEL ISOLATION
  └── Standard user privileges, no admin

Layer 5: DATA ISOLATION
  └── Per-user data folder, no shared state
```

---

## 7. Training Data Format

### intent_data.json
```json
{
  "intents": [
    {
      "tag": "open_app",
      "patterns": ["open {app}", "launch {app}", "start {app}"],
      "description": "User wants to open an application"
    }
  ]
}
```

### emotion_data.json
```json
{
  "emotions": {
    "sad": {
      "keywords": ["sad", "unhappy", "depressed"],
      "phrases": ["I feel sad", "I'm not okay"],
      "weight": 1.5
    }
  },
  "negation_words": ["not", "don't"],
  "intensifiers": {"very": 1.4, "extremely": 1.6}
}
```

### responses.json
```json
{
  "greeting": ["Hey there! How can I help?"],
  "emotion_responses": {
    "sad": ["I'm sorry you're feeling down..."]
  }
}
```

### knowledge_base.json
```json
{
  "entries": [
    {
      "question": "what is python",
      "answer": "Python is a popular programming language..."
    }
  ]
}
```

**To train the AI:** Simply add more entries to these JSON files.

---

## 8. Installation & Setup

### Prerequisites
- Windows 10/11
- Python 3.8+ (for development only; not needed after packaging)
- A microphone (optional — text mode available)

### Steps

```bash
# 1. Navigate to the project
cd OfflineAI

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# Optional: install FER-based camera emotion model
pip install -r requirements_vision.txt

# 4. Run in text mode
python main.py --text

# 5. Run with voice
python main.py

# 6. Run Jarvis web UI (browser)
python jarvis_app.py

# 7. Run Jarvis desktop app (native window)
python jarvis_app.py --desktop
```

### PyAudio Installation (if pip fails)

```bash
# Option A: Use pipwin
pip install pipwin
pipwin install pyaudio

# Option B: Download .whl from
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# then: pip install PyAudio‑0.2.13‑cp311‑cp311‑win_amd64.whl
```

---

## 9. JARVIS Visual App (Desktop + Web + Hybrid Models)

The project now includes a visual JARVIS runtime with:

- Face-to-face UI with live camera preview
- Procedural 3D avatar renderer with automatic fallback to 2D avatar
- Animated male/female avatar with emotion-driven expressions
- Interactive image portal with depth-tilt/parallax reaction to human movement
- Tamil + English conversation flow
- Camera-based visual emotion pipeline (OpenCV + optional FER model)
- Offline + online model routing modes: `offline`, `online`, `hybrid`, `auto`
- Speed profiles for response tuning: `turbo`, `balanced`, `quality`
- Bilingual response optimizer with compact context windows + response cache
- Optional desktop app mode via `pywebview`

### Run Modes

```bash
# Browser mode
python jarvis_app.py

# Desktop window mode
python jarvis_app.py --desktop

# Custom host/port
python jarvis_app.py --host 127.0.0.1 --port 9000
```

### Online Model Configuration (Optional)

If no online provider is configured, Jarvis continues in offline mode automatically.

```powershell
# OpenAI
setx OPENAI_API_KEY "your_api_key_here"
setx OPENAI_MODEL "gpt-4o-mini"

# Ollama (local)
setx OLLAMA_BASE_URL "http://127.0.0.1:11434"
setx OLLAMA_MODEL "llama3.1"

# Optional: force billion-model runtime path
setx JARVIS_USE_BILLION_MODEL "1"
setx JARVIS_BILLION_MODEL "jarvis-bilingual-1b"
setx JARVIS_SPEED_PROFILE "balanced"
```

Restart terminal after `setx` commands.

### Camera Emotion Notes

- Base vision pipeline works with OpenCV from `requirements.txt`
- Higher-accuracy FER inference is enabled when `requirements_vision.txt` is installed
- If FER is unavailable, Jarvis automatically falls back to OpenCV face detection + neutral-safe inference

---

## 10. Building the Executable

```bash
# Make sure PyInstaller is installed
pip install pyinstaller

# Build original OfflineAI console assistant
python build.py

# Build Jarvis web/desktop runtime
python build_jarvis.py
```

This creates:
```
dist/
  OfflineAI/         ← Original console assistant build
  JarvisAI/          ← Jarvis visual app build
    JarvisAI.exe
    Start-JARVIS-Desktop.bat
    Start-JARVIS-Web.bat
    data/
      user/
    jarvis/
      static/
    ...
```

### Build One-Click Windows Installer (JarvisAI)

```powershell
powershell -ExecutionPolicy Bypass -File .\build_installer.ps1
```

This generates a setup executable under:

```
installer/Output/JarvisAI-Setup.exe
```

**No Python installation is needed on the target machine.**

---

## 11. Viva Q&A — Key Explanations

### Q: "Why does small data work?"

**A:** This system solves a *narrow, well-defined* set of problems — not a general intelligence challenge. We only need to:
- Match against ~15 intent patterns
- Match against ~150 emotion keywords
- Search ~20 knowledge base entries

For these tasks, **pattern matching and fuzzy string comparison** are sufficient. We don't need millions of data points because our problem space is small and predictable. A user asking to "open Notepad" will always use similar words. This is fundamentally different from ChatGPT, which must understand all human knowledge.

**Analogy:** A calculator doesn't need AI to add 2+2. Similarly, matching "open Notepad" to the `open_app` intent doesn't need deep learning.

### Q: "Why is offline AI safer?"

**A:**
1. **No data leaves the computer** — impossible to leak information
2. **No external dependencies** — can't be compromised by a cloud provider breach
3. **No telemetry** — the AI doesn't report anything to anyone
4. **Deterministic behavior** — the AI can only do what's explicitly in its whitelist
5. **Auditable** — all code and data files are readable, inspectable JSON
6. **No adversarial attacks** — online AI can be prompt-injected; ours cannot be remotely manipulated

### Q: "What's the difference between global AI and local AI?"

| Aspect | Global AI (ChatGPT) | Local AI (OfflineAI) |
|---|---|---|
| Data source | Billions of web pages | Developer-created JSON files |
| Training | Massive GPU clusters, weeks | Edit a JSON file, instant |
| Knowledge | Vast but can hallucinate | Limited but 100% accurate |
| Privacy | Data sent to cloud | Data never leaves PC |
| Internet | Required | Not needed |
| Cost | Subscription / API fees | Free |
| Control | Owned by a company | Owned by the user |
| Scope | General-purpose | Task-specific |

### Q: "Why is this system ethical?"

1. **Transparency** — the AI admits when it doesn't know something
2. **No manipulation** — never says "only I understand you" or creates dependency
3. **Encourages human interaction** — designed to support, not replace, relationships
4. **No data collection** — respects privacy by design
5. **No deception** — never generates fake answers; says "I don't know"
6. **User control** — the user owns their data and can delete it anytime

### Q: "How is security ensured?"

Security follows the **principle of least privilege**:
1. Only whitelisted commands execute
2. Input is validated against blocked keywords
3. No admin privileges — runs as normal user
4. No filesystem access beyond its own data folder
5. No network access
6. All code is open and auditable

### Q: "Can this system be extended?"

Yes! Possible extensions (without breaking offline constraint):
- Add more intent patterns to `intent_data.json`
- Add Q&A pairs to `knowledge_base.json`
- Add new whitelisted apps in `config.py`
- Use Vosk instead of PocketSphinx (better accuracy, still offline)
- Add a simple GUI with tkinter (built into Python)
- Add wake word detection ("Hey Assistant")

---

## 12. Ethics & Limitations

### What the AI DOES:
- Executes safe, pre-approved commands
- Provides empathetic emotional support
- Answers questions from its knowledge base
- Learns from user-taught Q&A pairs
- Remembers user preferences locally

### What the AI DOES NOT do:
- Browse the internet
- Collect or transmit any data
- Access passwords, personal files, or credentials
- Run as administrator
- Delete, modify, or access system files
- Monitor user behavior in the background
- Pretend to know things it doesn't

### Ethical Safeguards Built In:
- **Honesty:** "I don't know that yet. You can teach me if you want."
- **No dependency creation:** Never says "only I can help you"
- **Encourages real help:** For serious emotional distress, a future version should recommend professional help
- **User sovereignty:** All data is local, deletable, and inspectable

---

## 13. Future Enhancements

| Enhancement | Difficulty | Offline? |
|---|---|---|
| Vosk speech engine (better accuracy) | Easy | ✅ Yes |
| Tkinter GUI with chat interface | Medium | ✅ Yes |
| Wake word ("Hey Assistant") | Medium | ✅ Yes |
| Scheduled reminders/alarms | Easy | ✅ Yes |
| Multi-language support | Medium | ✅ Yes |
| Conversation context (multi-turn) | Medium | ✅ Yes |
| File organizer (safe, whitelisted) | Medium | ✅ Yes |
| Screen reader integration | Hard | ✅ Yes |

---

## 14. Billion-Model Fine-Tuning (Tamil + English)

You can train a compact bilingual Jarvis model (1B-3B range) using a memory-efficient QLoRA workflow.

### Install training dependencies

```bash
pip install -r requirements_training.txt
```

### Prepare training data

Use JSONL rows with this shape:

```json
{"user": "How are you?", "assistant": "I'm good.", "language": "en", "emotion": "happy"}
```

Starter data is available at:
- `data/training_conversations.sample.jsonl`

### Train a bilingual 1B model

```bash
python train_billion_jarvis.py \
  --base-model Qwen/Qwen2.5-1.5B-Instruct \
  --dataset data/training_conversations.sample.jsonl \
  --output-dir models/jarvis-bilingual-1b \
  --epochs 2
```

### Runtime integration

After exporting your trained model for local runtime, point Jarvis to it with:

```powershell
setx JARVIS_USE_BILLION_MODEL "1"
setx JARVIS_BILLION_MODEL "jarvis-bilingual-1b"
```

Jarvis will then prefer that model in online/Ollama path while still keeping low-latency fallback logic.

---

## Project File Structure

```
OfflineAI/
├── main.py                          ← Entry point
├── jarvis_app.py                    ← Jarvis web + desktop runtime
├── config.py                        ← All constants & paths
├── requirements.txt                 ← Python dependencies
├── requirements_vision.txt          ← Optional FER/TensorFlow extras
├── requirements_training.txt        ← Optional QLoRA training dependencies
├── build.py                         ← PyInstaller build script
├── build_jarvis.py                  ← Jarvis executable build script
├── build_installer.ps1              ← Inno Setup installer automation
├── train_billion_jarvis.py          ← Billion-model bilingual fine-tuning script
├── README.md                        ← This documentation
├── __init__.py
│
├── modules/
│   ├── __init__.py
│   ├── voice_input.py               ← Module 1: Mic → Text
│   ├── intent_detector.py           ← Module 2: Intent classification
│   ├── emotion_detector.py          ← Module 3: Emotion detection
│   ├── decision_engine.py           ← Module 4: Core brain
│   ├── command_executor.py          ← Module 5: Safe OS commands
│   ├── response_engine.py           ← Module 6: Response templates
│   ├── knowledge_base.py            ← Module 7: Offline Q&A
│   ├── memory.py                    ← Module 8: Local persistence
│   ├── voice_output.py              ← Module 9: Text → Speech
│   ├── model_router.py              ← Module 10: Online model routing
│   ├── vision_emotion.py            ← Module 11: Camera emotion pipeline
│   └── bilingual_optimizer.py       ← Module 13: Fast bilingual optimization
│
├── jarvis/
│   └── static/
│       ├── index.html               ← Jarvis visual interface
│       ├── styles.css               ← Futuristic avatar/UI theme
│       └── app.js                   ← Frontend logic + API integration
│
├── installer/
│   ├── JarvisAI.iss                 ← Inno Setup script
│   └── Output/                      ← Generated installer output
│
├── data/
│   ├── intent_data.json             ← Intent patterns (trainable)
│   ├── emotion_data.json            ← Emotion keywords (trainable)
│   ├── responses.json               ← AI response templates
│   ├── knowledge_base.json          ← Q&A knowledge (teachable)
│   ├── training_conversations.sample.jsonl  ← Bilingual training sample
│   └── user/
│       └── memory.json              ← Per-user memory & history
│
├── logs/                            ← (optional) log files
└── dist/                            ← (after build) .exe output
```

---

*Developed as a final-year engineering project. Fully open, auditable, and offline.*
