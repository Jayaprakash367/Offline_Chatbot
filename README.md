# Offline_Chatbot

A fully **offline**, privacy-first AI assistant for Windows — no internet required after setup.  
Supports both **voice** (microphone + speaker) and **text** interaction modes.

---

## Features

- 🔒 **Fully Offline** — no internet connection required at runtime
- 🎙️ **Voice & Text Modes** — switch between microphone input or keyboard input
- 🧠 **Emotion-Aware** — detects user emotion and responds empathetically
- 🗂️ **Memory** — remembers your name and conversation history across sessions
- 🖥️ **System Controls** — open/close apps, check CPU, RAM and battery
- 📚 **Teachable** — teach the assistant new Q&A pairs on the fly
- 🛡️ **Secure** — blocked keywords and input length limits prevent misuse
- 📦 **Standalone Executable** — can be packaged as a Windows `.exe` via PyInstaller

---

## Tech Stack

| Component | Library |
|---|---|
| Offline Speech-to-Text | [Vosk](https://alphacephei.com/vosk/) |
| Text-to-Speech | [pyttsx3](https://pypi.org/project/pyttsx3/) (Windows SAPI5) |
| Microphone Access | [PyAudio](https://pypi.org/project/PyAudio/) |
| System Monitoring | [psutil](https://pypi.org/project/psutil/) |
| Speech Recognition helper | [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) |

---

## Project Structure

```
Offline_Chatbot/
└── OfflineAI/
    ├── main.py                  # Entry point — runs the assistant
    ├── config.py                # App-wide configuration and constants
    ├── requirements.txt         # Python dependencies
    ├── build.py                 # PyInstaller build script (Windows .exe)
    ├── VOICE_MODE_GUIDE.md      # Tips for improving voice recognition
    ├── data/
    │   ├── intent_data.json     # Intent detection training data
    │   ├── emotion_data.json    # Emotion detection training data
    │   ├── responses_en.json    # English response templates
    │   ├── knowledge_base.json  # Q&A knowledge base
    │   └── user/                # Per-user memory (created at runtime)
    └── modules/
        ├── voice_input.py       # Microphone → text (Vosk)
        ├── voice_output.py      # Text → speech (pyttsx3)
        ├── decision_engine.py   # Core brain — orchestrates all modules
        ├── intent_detector.py   # Classify user intent
        ├── emotion_detector.py  # Detect user emotion
        ├── command_executor.py  # Open/close apps, system status
        ├── response_engine.py   # Pick and format responses
        ├── knowledge_base.py    # Search and store Q&A facts
        └── memory.py            # Persistent user memory
```

---

## Requirements

- **Windows 10 / 11** (pyttsx3 uses Windows SAPI5; other platforms are not supported)
- **Python 3.8+**
- A working **microphone** (voice mode only)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Jayaprakash367/Offline_Chatbot.git
   cd Offline_Chatbot/OfflineAI
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Vosk speech model** (for voice mode)

   Download [`vosk-model-small-en-us-0.15`](https://alphacephei.com/vosk/models) and extract it into:

   ```
   OfflineAI/vosk-model/
   ```

---

## Usage

### Voice Mode (default)

Speak into your microphone — the assistant listens, processes, and speaks back.

```bash
python main.py
```

### Text Mode

Type your commands using the keyboard — no microphone needed.

```bash
python main.py --text
# or
python main.py -t
```

> The assistant automatically falls back to text mode if no microphone is detected.

---

## Example Commands

| Category | Example Phrases |
|---|---|
| Greeting | `hello`, `good morning`, `good evening` |
| Time & Date | `what time is it`, `what is today's date` |
| Open Apps | `open notepad`, `open calculator`, `open brave` |
| Close Apps | `close chrome`, `close notepad` |
| System Status | `system status`, `check CPU` |
| Jokes | `tell me a joke` |
| Questions | `what is Python` |
| Teach New Facts | `teach` → then `What is X \| X is ...` |
| Exit | `bye`, `exit`, `quit` |

---

## Building a Standalone Executable

Use the included build script to create a Windows `.exe` (requires [PyInstaller](https://pyinstaller.org)):

```bash
python build.py
```

The executable will be created at `dist/OfflineAI/OfflineAI.exe` and can be run on any Windows PC without Python installed.

---

## Voice Mode Tips

For best voice recognition accuracy:

- Speak clearly and at a natural pace
- Use the assistant in a quiet environment
- Keep the microphone 6–8 inches away
- Use simple, direct phrases (e.g. `"open notepad"` rather than `"could you maybe open notepad for me"`)
- If recognition fails, type `y` to retry or `t` to switch to text input

See [`VOICE_MODE_GUIDE.md`](OfflineAI/VOICE_MODE_GUIDE.md) for detailed guidance.

---

## Security

The assistant enforces several safety measures:

- **Input length limit** — inputs longer than 500 characters are rejected
- **Blocked keywords** — dangerous keywords (e.g. `delete`, `format`, `registry`, `hack`) are blocked
- **Whitelisted apps** — only explicitly allowed applications can be opened or closed

---

## License

This project is open-source. See the repository for license details.
