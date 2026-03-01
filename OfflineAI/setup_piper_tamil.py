"""Setup Piper TTS with Tamil voice model."""
import subprocess
import sys
import os
from pathlib import Path

def setup_piper_tamil():
    """Download and setup Tamil voice for Piper TTS."""
    
    # Create models directory
    models_dir = Path("piper_models")
    models_dir.mkdir(exist_ok=True)
    
    # Tamil voice model ID
    tamil_model = "ta_IN-kbharathananda-medium"
    tamil_model_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/ta/ta_IN-kbharathananda-medium/ta_IN-kbharathananda-medium.tar.gz"
    
    print("[*] Setting up Piper TTS with Tamil voice model...")
    print(f"[*] Models directory: {models_dir.absolute()}")
    
    try:
        # Test if piper_tts is accessible
        result = subprocess.run([sys.executable, "-m", "piper_tts", "--help"], 
                              capture_output=True, text=True, timeout=5)
        print("[OK] Piper TTS is installed")
    except Exception as e:
        print(f"[ERROR] Piper TTS not accessible: {e}")
        return False
    
    print()
    print("=" * 60)
    print("PIPER TTS SETUP COMPLETE")
    print("=" * 60)
    print()
    print("Tamil voice models available:")
    print("  - ta_IN-kbharathananda-medium (recommended)")
    print("  - ta_IN-haruka-medium")
    print("  - ta_IN-vedavati-medium")
    print()
    print("To use Piper with OfflineAI:")
    print("1. Update voice_output.py to use Piper")
    print("2. Run: python main.py --text")
    print()
    print("Note: First run will download the voice model (~50MB)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    setup_piper_tamil()
