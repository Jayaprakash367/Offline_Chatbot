"""
=============================================================
  MODULE 9 — VOICE OUTPUT (Offline Text-to-Speech)
  Uses pyttsx3 for English (Windows SAPI5)
  Fully offline — no network calls.
  NEVER stores generated audio.
=============================================================
"""

import pyttsx3
from config import VOICE_RATE, VOICE_VOLUME, PREFERRED_VOICE_NAME, FALLBACK_VOICE_NAME


class VoiceOutput:
    """Converts text to speech using pyttsx3 (English voices via Windows SAPI5)."""

    def __init__(self):
        self.engine = None
        self._tts_available = False
        self._init_engine()

    def _init_engine(self):
        """Initialise the pyttsx3 TTS engine with robust error handling."""
        try:
            self.engine = pyttsx3.init("sapi5")
            self._configure()
            self._tts_available = True
            print("[VoiceOutput] TTS engine ready")
        except Exception as e:
            print(f"[VoiceOutput] pyttsx3 init failed: {e}")
            try:
                self.engine = pyttsx3.init()
                self._configure()
                self._tts_available = True
                print("[VoiceOutput] TTS engine ready (fallback driver)")
            except Exception as e2:
                print(f"[VoiceOutput] TTS unavailable: {e2}")
                self._tts_available = False

    # ── public API ────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Speak the given text aloud and print it."""
        if not text:
            return
        print(f"\n  AI: {text}")

        if self._tts_available:
            self._speak_pyttsx3(text)

    def _speak_pyttsx3(self, text: str) -> None:
        """Speak text using pyttsx3 (English voices)."""
        if not self._tts_available:
            return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            try:
                self._init_engine()
                if self._tts_available:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception:
                pass
        except Exception as e:
            print(f"  [TTS error: {e}]")

    def set_rate(self, rate: int) -> None:
        """Change speech speed (words per minute)."""
        if self._tts_available and self.engine:
            self.engine.setProperty("rate", rate)

    def set_volume(self, vol: float) -> None:
        """Change volume (0.0 - 1.0)."""
        if self._tts_available and self.engine:
            self.engine.setProperty("volume", max(0.0, min(1.0, vol)))

    # ── private helpers ───────────────────────────────────

    def _configure(self) -> None:
        """Apply default voice settings."""
        if not self.engine:
            return

        self.engine.setProperty("rate", VOICE_RATE)
        self.engine.setProperty("volume", VOICE_VOLUME)

        voices = self.engine.getProperty("voices")
        if not voices:
            return

        # 1st priority: preferred voice (e.g. "David")
        for v in voices:
            if PREFERRED_VOICE_NAME.lower() in v.name.lower():
                self.engine.setProperty("voice", v.id)
                print(f"  Selected voice: {v.name}")
                return

        # 2nd priority: fallback voice (e.g. "Zira")
        for v in voices:
            if FALLBACK_VOICE_NAME.lower() in v.name.lower():
                self.engine.setProperty("voice", v.id)
                print(f"  Selected voice: {v.name}")
                return

        # Last resort: first available
        if voices:
            self.engine.setProperty("voice", voices[0].id)
            print(f"  Selected voice: {voices[0].name}")
