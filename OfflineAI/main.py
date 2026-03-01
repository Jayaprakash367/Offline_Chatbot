"""
=============================================================
  MAIN.PY — Entry Point for OfflineAI
  
  A fully offline, secure, emotion-aware Windows AI assistant.
  
  Run modes:
    python main.py            →  Voice mode (mic + speaker)
    python main.py --text     →  Text-only mode (keyboard)
  
  This file wires together ALL 9 modules and runs the
  main interaction loop.
=============================================================
"""

import sys
import os
import argparse

# Ensure the project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import APP_NAME, APP_VERSION
from modules.voice_input import VoiceInput
from modules.voice_output import VoiceOutput
from modules.decision_engine import DecisionEngine


# ─── Banner ──────────────────────────────────────────────

BANNER = rf"""
=====================================================
     {APP_NAME} v{APP_VERSION}
     Offline AI Assistant - English Only
=====================================================
     * Fully Offline   * Voice & Text   * Secure

     USAGE:
       python main.py           → Voice/Speaking Mode (mic → speaker)
       python main.py --text    → Text Mode (keyboard → text)

     Commands:
       'help'  - show available commands
       'bye'   - exit
       Ctrl+C  - quit
=====================================================
"""

HELP_TEXT = """
Available commands:
- Open/close apps (notepad, calc, brave, edge, explorer, etc.)
- Check system status (CPU, RAM, battery)
- Tell jokes
- Answer questions
- Get current time and date
- System management
- And much more!
"""

EXIT_KEYWORDS = ["bye", "exit", "quit", "goodbye", "poweroff", "shutdown"]


def parse_args():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} — Offline AI Assistant")
    parser.add_argument(
        "--text", "-t",
        action="store_true",
        help="Run in text-only mode (no microphone needed)",
    )
    return parser.parse_args()


def text_input_loop(engine: DecisionEngine, voice_out: VoiceOutput):
    """Text-only interaction loop."""
    while True:
        try:
            user_input = input("\n  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            voice_out.speak("Goodbye! See you soon!")
            break

        if not user_input:
            continue

        # Exit keywords
        if user_input.lower() in EXIT_KEYWORDS:
            voice_out.speak("Goodbye! See you soon!")
            break

        response = engine.process(user_input)
        voice_out.speak(response)


def voice_input_loop(engine: DecisionEngine, voice_in: VoiceInput, voice_out: VoiceOutput):
    """Voice-based interaction loop (microphone input)."""
    # Show tips for better voice recognition
    print("\n" + "=" * 60)
    print("  VOICE MODE TIPS for best recognition:")
    print("  - Speak clearly and naturally")
    print("  - Keep background noise low")
    print("  - Take short pauses between sentences")
    print("  - If misheard, say 'y' when prompted to retry")
    print("  - Or type your command directly")
    print("=" * 60)
    
    while True:
        try:
            user_input = voice_in.listen()
        except KeyboardInterrupt:
            voice_out.speak("Goodbye! See you soon!")
            break

        if not user_input:
            continue

        # Exit keywords
        if user_input.lower() in EXIT_KEYWORDS:
            voice_out.speak("Goodbye! See you soon!")
            break

        response = engine.process(user_input)
        voice_out.speak(response)


def main():
    args = parse_args()

    print(BANNER)

    # Initialise core modules
    engine = DecisionEngine()
    voice_out = VoiceOutput()

    # Welcome message
    name = engine.memory.get_user_name()
    if name:
        voice_out.speak(f"Hello {name}! How can I assist you?")
    else:
        voice_out.speak("Hello! I'm your offline AI assistant. What's your name?")
        # Get name
        if args.text:
            try:
                name_input = input("\n  You: ").strip()
            except (EOFError, KeyboardInterrupt):
                name_input = ""
        else:
            voice_in_temp = VoiceInput()
            name_input = voice_in_temp.listen()

        if name_input:
            engine.memory.set_user_name(name_input)
            voice_out.speak(f"Nice to meet you, {name_input}! I'm here to help.")

    # Main loop
    if args.text:
        text_input_loop(engine, voice_out)
    else:
        voice_in = VoiceInput()
        if not voice_in.is_mic_available():
            print("\n[INFO] Microphone not available. Switching to text mode.\n")
            text_input_loop(engine, voice_out)
        else:
            voice_input_loop(engine, voice_in, voice_out)

    print("\n  Session ended. See you soon!\n")


if __name__ == "__main__":
    main()
