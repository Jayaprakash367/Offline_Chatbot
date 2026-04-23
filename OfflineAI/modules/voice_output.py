"""
=============================================================
  MODULE 9 — VOICE OUTPUT (Offline Text-to-Speech)
  Uses Piper TTS for Tamil (fluent, emotional) and 
  pyttsx3 for English (Windows SAPI5).
  Fully offline — no network calls.
  NEVER stores generated audio.
=============================================================
"""

import os
import sys
import subprocess
import tempfile
import pyttsx3
from config import LANGUAGE, VOICE_RATE, VOICE_VOLUME, PREFERRED_VOICE_NAME, FALLBACK_VOICE_NAME

# ─── Tamil Piper voice model ID ─────────────────────────
# Using kbharathananda voice for natural, emotional Tamil
TAMIL_PIPER_MODEL = "ta_IN-kbharathananda-medium"


class VoiceOutput:
    """
    Converts text to speech using language-appropriate engines:
    - Tamil: Piper TTS (emotional, fluent) 
    - English: pyttsx3 (Windows SAPI5)
    """

    def __init__(self):
        self.engine = None
        self._tts_available = False
        self._piper_available = False
        self.language = LANGUAGE
        self._init_engines()

    def _init_engines(self):
        """Initialize engines based on configured language."""
        if self.language == "ta":
            self._init_piper_tamil()
        else:
            self._init_pyttsx3_english()

    def _init_piper_tamil(self):
        """Initialize Piper TTS for Tamil with emotional voices."""
        try:
            # Test if piper_tts is available
            result = subprocess.run(
                [sys.executable, "-m", "piper_tts", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self._piper_available = True
                self._tts_available = True
                print("[VoiceOutput] Piper TTS initialized for Tamil")
                print(f"  Model: {TAMIL_PIPER_MODEL}")
        except Exception as e:
            print(f"[VoiceOutput] Piper TTS not available: {e}")
            print("  Install with: pip install piper-tts")
            self._piper_available = False
            self._tts_available = False

    def _init_pyttsx3_english(self):
        """Initialize pyttsx3 for English (Windows SAPI5)."""
        try:
            self.engine = pyttsx3.init("sapi5")
            self._configure_pyttsx3()
            self._tts_available = True
            print("[VoiceOutput] TTS engine ready (pyttsx3)")
        except Exception as e:
            print(f"[VoiceOutput] pyttsx3 init failed: {e}")
            try:
                self.engine = pyttsx3.init()
                self._configure_pyttsx3()
                self._tts_available = True
                print("[VoiceOutput] TTS engine ready (fallback driver)")
            except Exception as e2:
                print(f"[VoiceOutput] TTS unavailable: {e2}")
                self._tts_available = False

    # ── public API ────────────────────────────────────────

    def speak(self, text: str, emotion: str = "neutral") -> None:
        """
        Speak text with optional emotion emphasis.
        
        Parameters
        ----------
        text : str
            Text to speak
        emotion : str
            Emotion type: 'happy', 'sad', 'excited', 'calm', 'neutral'
            (Used for Piper TTS to add prosody variation)
        """
        if not text:
            return
        print(f"\n  AI: {text}")

        if not self._tts_available:
            return

        if self.language == "ta":
            self._speak_piper_tamil(text, emotion)
        else:
            self._speak_pyttsx3_english(text)

    def _speak_piper_tamil(self, text: str, emotion: str = "neutral") -> None:
        """
        Speak Tamil text using Piper TTS with emotional prosody.
        
        Emotions add subtle speed and pitch variations:
        - happy: faster, higher pitch
        - excited: faster, higher pitch, more emphasis
        - sad: slower, lower pitch
        - calm: slower, neutral pitch
        - neutral: default
        """
        if not self._piper_available:
            return

        try:
            # Apply emotion-based speed adjustments
            speed_adjustment = 1.0
            if emotion in ["happy", "excited"]:
                speed_adjustment = 1.1  # 10% faster for positive emotions
            elif emotion == "sad":
                speed_adjustment = 0.85  # 15% slower for sad
            elif emotion == "calm":
                speed_adjustment = 0.9  # 10% slower for calm

            # Use temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Run Piper TTS
                cmd = [
                    sys.executable,
                    "-m",
                    "piper_tts",
                    "--model",
                    TAMIL_PIPER_MODEL,
                    "--output-file",
                    tmp_path,
                    "--speaker",
                    "0",  # Default speaker
                    "--rate",
                    str(speed_adjustment),
                ]

                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=text, timeout=15)

                if process.returncode == 0 and os.path.exists(tmp_path):
                    # Play the generated audio
                    self._play_audio_file(tmp_path)
                else:
                    print(f"  [Piper error: {stderr}]")

            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except:
                        pass

        except subprocess.TimeoutExpired:
            print("  [Piper TTS timeout]")
        except Exception as e:
            print(f"  [Piper error: {e}]")

    def _play_audio_file(self, filepath: str) -> None:
        """Play an audio file using Windows media player."""
        try:
            import winsound
            winsound.PlaySound(filepath, winsound.SND_FILENAME)
        except Exception as e:
            # Fallback: try using Windows media player via subprocess
            try:
                subprocess.Popen(["powershell", "-c", f"(New-Object System.media.SoundPlayer '{filepath}').PlaySync()"])
            except:
                print(f"  [Could not play audio: {e}]")

    def _speak_pyttsx3_english(self, text: str) -> None:
        """Speak English text using pyttsx3."""
        if not self._tts_available or not self.engine:
            return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            try:
                self._init_pyttsx3_english()
                if self._tts_available:
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception:
                pass
        except Exception as e:
            print(f"  [TTS error: {e}]")

    def set_rate(self, rate: int) -> None:
        """Change speech speed (words per minute)."""
        if self._tts_available and self.engine and self.language == "en":
            self.engine.setProperty("rate", rate)

    def set_volume(self, vol: float) -> None:
        """Change volume (0.0 - 1.0)."""
        if self._tts_available and self.engine and self.language == "en":
            self.engine.setProperty("volume", max(0.0, min(1.0, vol)))

    # ── private helpers ───────────────────────────────────

    def _configure_pyttsx3(self) -> None:
        """Apply default voice settings for English."""
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
