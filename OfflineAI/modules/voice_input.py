"""
=============================================================
  MODULE 1 — VOICE INPUT (Offline Speech Recognition)
  
  Uses the VOSK engine for high-accuracy offline recognition.
  Auto-downloads the small English model on first run.
  Falls back to TEXT input if mic/model unavailable.
  NEVER records or stores raw audio.
=============================================================
"""

import os
import sys
import json
import struct
import speech_recognition as sr
from config import LANGUAGE

# ─── Resolve model path ─────────────────────────────────
if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VOSK_MODEL_PATH = os.path.join(_BASE, "vosk-model")


def _download_vosk_model():
    """Download the small English Vosk model (~40 MB) on first run."""
    if os.path.isdir(VOSK_MODEL_PATH):
        return True

    print("\n" + "=" * 55)
    print("  First-time setup: Downloading speech model (~40 MB)")
    print("  This only happens ONCE. Please wait...")
    print("=" * 55)

    import urllib.request
    import zipfile

    url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    zip_path = os.path.join(_BASE, "vosk-model.zip")
    extract_name = "vosk-model-small-en-us-0.15"

    try:
        urllib.request.urlretrieve(url, zip_path)
        print("  Extracting model...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(_BASE)
        os.rename(os.path.join(_BASE, extract_name), VOSK_MODEL_PATH)
        os.remove(zip_path)
        print("  Speech model ready!\n")
        return True
    except Exception as e:
        print(f"\n  Could not download model: {e}")
        print("  You can manually download from:")
        print(f"    {url}")
        print(f"  Extract to: {VOSK_MODEL_PATH}")
        print("  Falling back to text input.\n")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return False


class VoiceInput:
    """Captures user speech via Vosk (offline) or keyboard fallback."""

    def __init__(self):
        self._vosk_available = False
        self._mic_available = False
        self._model = None
        self._pyaudio = None

        # 1. Try to load Vosk
        try:
            from vosk import Model, SetLogLevel
            SetLogLevel(-1)  # suppress Vosk debug logs

            if os.path.isdir(VOSK_MODEL_PATH):
                self._model = Model(VOSK_MODEL_PATH)
                self._vosk_available = True
                print("[VoiceInput] Vosk model loaded")
            else:
                # Try auto-download
                if _download_vosk_model():
                    self._model = Model(VOSK_MODEL_PATH)
                    self._vosk_available = True
                    print("[VoiceInput] Vosk model loaded")
        except ImportError:
            print("[VoiceInput] Vosk not installed. Using text input.")
        except Exception as e:
            print(f"[VoiceInput] Vosk init error: {e}")

        # 2. Try to init PyAudio for mic access
        try:
            import pyaudio
            self._pyaudio = pyaudio.PyAudio()
            # Quick test: can we open an input stream?
            if self._pyaudio is not None:
                test = self._pyaudio.open(
                    format=pyaudio.paInt16, channels=1,
                    rate=16000, input=True, frames_per_buffer=4096
                )
                test.close()
                self._mic_available = True
                print("[VoiceInput] Microphone ready")
        except Exception as e:
            print(f"[VoiceInput] No microphone: {e}")
            self._mic_available = False

        # 3. Try to init Google Speech Recognition for Tamil
        try:
            self._recognizer = sr.Recognizer()
            self._google_available = True
            print("[VoiceInput] Google Speech Recognition (Tamil) ready")
        except Exception as e:
            print(f"[VoiceInput] Google Speech Recognition init failed: {e}")
            self._google_available = False

    # ── public API ────────────────────────────────────────

    def listen(self) -> str:
        """Listen to the user and return recognised text."""
        if not self._mic_available or not self._vosk_available:
            return self._text_fallback()

        try:
            text = self._listen_vosk()
            
            # If no text recognized, offer retry or text fallback
            if not text:
                print("   [Tip] Speak clearly and try again, or type your command]")
                retry = input("   Retry (y) or type (t)? ").strip().lower()
                if retry == "y":
                    return self.listen()
                else:
                    return self._text_fallback()
            
            return text
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"   [Voice error: {e}]")
            return self._text_fallback()

    def is_mic_available(self) -> bool:
        if LANGUAGE == "ta":
            return self._mic_available and self._google_available
        else:
            return self._mic_available and self._vosk_available

    # ── Vosk-based listening ──────────────────────────────

    def _listen_vosk(self) -> str:
        """Record from mic and recognise with Vosk. High accuracy."""
        import pyaudio
        from vosk import KaldiRecognizer

        # Type safety: ensure PyAudio is initialized before use
        assert self._pyaudio is not None, "PyAudio not initialized"

        RATE = 16000
        CHUNK = 4096
        SILENCE_LIMIT = 1.5       # seconds of silence to stop (reduced from 2.0)
        MAX_DURATION = 10.0       # max recording seconds (reduced from 15.0)
        SILENCE_THRESHOLD = 400   # audio amplitude threshold (increased for better filtering)
        MIN_SPEECH_DURATION = 0.5 # minimum speech duration before recognition

        rec = KaldiRecognizer(self._model, RATE)

        stream = self._pyaudio.open(
            format=pyaudio.paInt16, channels=1,
            rate=RATE, input=True, frames_per_buffer=CHUNK
        )

        print("\n  Listening... (speak now)")

        silent_chunks = 0
        max_silent = int(SILENCE_LIMIT * RATE / CHUNK)
        max_chunks = int(MAX_DURATION * RATE / CHUNK)
        heard_speech = False
        speech_chunks = 0

        for i in range(max_chunks):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
            except Exception:
                continue

            # Detect if this chunk has sound
            amplitude = self._rms(data)
            if amplitude > SILENCE_THRESHOLD:
                heard_speech = True
                silent_chunks = 0
                speech_chunks += 1
            else:
                silent_chunks += 1

            # Feed to recogniser
            try:
                if rec.AcceptWaveform(data):
                    # Got a complete utterance
                    break
            except Exception:
                continue

            # Stop after sustained silence (only if we heard speech first)
            if heard_speech and silent_chunks > max_silent and speech_chunks > int(MIN_SPEECH_DURATION * RATE / CHUNK):
                break

        stream.stop_stream()
        stream.close()

        # Get final result
        try:
            result = json.loads(rec.FinalResult())
            text = result.get("text", "").strip()
        except Exception:
            text = ""

        if text:
            print(f"   You said: \"{text}\"")
        else:
            print("   [No speech detected - try speaking clearly]")

        return text

    def _listen_google_tamil(self) -> str:
        """Listen to Tamil speech using Google Speech Recognition."""
        try:
            with sr.Microphone() as source:
                print("\n  Listening... (speak Tamil now)")
                self._recognizer.adjust_for_ambient_noise(source)
                audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Recognize speech using Google with Tamil language
                text = self._recognizer.recognize_google(audio, language='ta-IN')  # type: ignore
                text = text.strip()

                if text:
                    print(f"   You said: \"{text}\"")
                else:
                    print("   [No speech detected]")

                return text
        except sr.WaitTimeoutError:
            print("   [No speech detected - timeout]")
            return ""
        except sr.UnknownValueError:
            print("   [Could not understand Tamil speech]")
            return ""
        except sr.RequestError as e:
            print(f"   [Google Speech Recognition error: {e}]")
            return ""
        except Exception as e:
            print(f"   [Tamil voice error: {e}]")
            return ""

    @staticmethod
    def _rms(data: bytes) -> float:
        """Calculate root-mean-square amplitude of audio chunk."""
        count = len(data) // 2
        if count == 0:
            return 0
        shorts = struct.unpack(f"<{count}h", data)
        sum_sq = sum(s * s for s in shorts)
        return (sum_sq / count) ** 0.5

    @staticmethod
    def _text_fallback() -> str:
        """Keyboard input fallback."""
        try:
            return input("\n  You (type): ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""
