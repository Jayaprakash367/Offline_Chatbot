"""
=============================================================
  OFFLINE AI ASSISTANT — CONFIGURATION
  All system-wide constants and paths.
  No internet, no cloud, no external APIs.
=============================================================
"""

import os
import sys

# ─── Language ─────────────────────────────────────────────
LANGUAGE = "en"  # "ta" = Tamil, "en" = English (ENGLISH ONLY NOW)

# ─── Paths ────────────────────────────────────────────────
APP_NAME = "OfflineAI"
APP_VERSION = "1.0.0"

# Base directory: works for both dev and frozen (PyInstaller) mode
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
USER_DATA_DIR = os.path.join(DATA_DIR, "user")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# JSON training / data files
INTENT_DATA_FILE = os.path.join(DATA_DIR, "intent_data.json")
EMOTION_DATA_FILE = os.path.join(DATA_DIR, "emotion_data.json")
RESPONSES_FILE = os.path.join(DATA_DIR, "responses.json")  # Tamil responses
RESPONSES_FILE_EN = os.path.join(DATA_DIR, "responses_en.json")  # English responses
KNOWLEDGE_BASE_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
MEMORY_FILE = os.path.join(USER_DATA_DIR, "memory.json")

# ─── Voice settings ──────────────────────────────────────
VOICE_RATE = 150          # words per minute for TTS
VOICE_VOLUME = 1.0        # 0.0 – 1.0
# For Tamil: install Windows Tamil language pack for Tamil TTS voice
# Settings > Time & Language > Language > Add Tamil > Download Speech pack
PREFERRED_VOICE_NAME = "David"  # Microsoft David (English)
FALLBACK_VOICE_NAME = "Zira"      # Microsoft Zira (English fallback)

# ─── Security — whitelisted applications ─────────────────
# Keys are canonical names; values are shell commands (no admin)
# Includes both English and Tamil/Romanized-Tamil aliases
WHITELISTED_APPS = {
    # System utilities
    "notepad":        "notepad.exe",
    "calculator":     "calc.exe",
    "calc":           "calc.exe",
    "paint":          "mspaint.exe",
    "file explorer":  "explorer.exe",
    "explorer":       "explorer.exe",
    "command prompt": "cmd.exe",
    "cmd":            "cmd.exe",
    "task manager":   "taskmgr.exe",
    "settings":       "ms-settings:",
    "control panel":  "control.exe",
    "snipping tool":  "snippingtool.exe",
    "clock":          "ms-clock:",
    "alarm":          "ms-clock:",
    # Browsers
    "chrome":         "chrome.exe",
    "google chrome":  "chrome.exe",
    "brave":          "brave.exe",
    "brave browser":  "brave.exe",
    "edge":           "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox":        "firefox.exe",
    "opera":          "opera.exe",
    # Code editors
    "vs code":        "code",
    "vscode":         "code",
    "visual studio code": "code",
    # Office
    "word":           "winword.exe",
    "excel":          "excel.exe",
    "powerpoint":     "powerpnt.exe",
    # Media
    "media player":   "wmplayer.exe",
    "vlc":            "vlc.exe",
    "spotify":        "spotify.exe",
    # Communication
    "teams":          "msteams.exe",
    "microsoft teams": "msteams.exe",
    "outlook":        "outlook.exe",
    "whatsapp":       "WhatsApp.exe",
    "telegram":       "Telegram.exe",
    "discord":        "discord.exe",
    "zoom":           "zoom.exe",
    # Other
    "terminal":       "wt.exe",
    "windows terminal": "wt.exe",
    "store":          "ms-windows-store:",
    "photos":         "ms-photos:",
}

# Applications that can be closed via taskkill (no admin)
CLOSEABLE_APPS = {
    "notepad":      "notepad.exe",
    "calculator":   "calculatorapp.exe",
    "paint":        "mspaint.exe",
    "chrome":       "chrome.exe",
    "google chrome": "chrome.exe",
    "brave":        "brave.exe",
    "brave browser": "brave.exe",
    "edge":         "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox":      "firefox.exe",
    "opera":        "opera.exe",
    "word":         "winword.exe",
    "excel":        "excel.exe",
    "powerpoint":   "powerpnt.exe",
    "vs code":      "code.exe",
    "vscode":       "code.exe",
    "visual studio code": "code.exe",
    "media player": "wmplayer.exe",
    "vlc":          "vlc.exe",
    "spotify":      "spotify.exe",
    "teams":        "msteams.exe",
    "outlook":      "outlook.exe",
    # Tamil aliases
    "\u0ba8\u0bcb\u0b9f\u0bcd\u0baa\u0bc7\u0b9f\u0bcd":       "notepad.exe",
    "\u0b95\u0bbe\u0bb2\u0bcd\u0b95\u0bc1\u0bb2\u0bc7\u0b9f\u0bcd\u0b9f\u0bb0\u0bcd":    "calculatorapp.exe",
    "\u0baa\u0bc6\u0baf\u0bbf\u0ba3\u0bcd\u0b9f\u0bcd":       "mspaint.exe",
    "\u0b95\u0bc1\u0bb0\u0bcb\u0bae\u0bcd":         "chrome.exe",
    "\u0baa\u0bcd\u0bb0\u0bc7\u0bb5\u0bcd":         "brave.exe",
    "\u0b8e\u0b9f\u0bcd\u0b9c\u0bcd":           "msedge.exe",
}

# ─── Safety constants ────────────────────────────────────
MAX_INPUT_LENGTH = 500           # chars
BLOCKED_KEYWORDS = [
    "delete", "format", "registry", "regedit", "powershell",
    "admin", "sudo", "rm -rf", "shutdown", "restart",
    "hack", "exploit", "inject", "keylog", "password",
    "virus", "malware", "trojan", "backdoor",
]

# ─── Emotion thresholds ──────────────────────────────────
EMOTION_CONFIDENCE_THRESHOLD = 0.3   # minimum score to classify

# ─── Memory limits ───────────────────────────────────────
MAX_MEMORY_ENTRIES = 200
MAX_CONVERSATION_HISTORY = 50

# ─── Ensure directories exist ────────────────────────────
for d in [DATA_DIR, USER_DATA_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)
