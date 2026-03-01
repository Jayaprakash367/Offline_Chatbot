# Tamil Voice Setup Guide for OfflineAI

## Current Status
- **Voice Recognition (Input)**: English only (Vosk limitation - no Tamil model available)
- **Text-to-Speech (Output)**: Currently falls back to Microsoft Zira (English voice)
- **Language Mode**: Tamil (responses in Tamil text)

## How to Add Tamil Voice Support

### Option 1: Using Google Translate Offline (Recommended for Tamil)
Tamil TTS is not natively available in Windows by default. Here are your options:

### Option 2: Install NVDA with Tamil Support
NVDA (NonVisual Desktop Access) has Tamil voice support:

1. Download NVDA: https://www.nvaccess.org/download/
2. Install it
3. Download Tamil language pack from NVDA Add-ons store
4. Integrate with OfflineAI via command-line

### Option 3: Use espeak-ng (Free, Lightweight)
espeak-ng is an open-source TTS engine with Tamil support:

#### Installation Steps:

1. **Install espeak-ng:**
   ```bash
   pip install espeak-ng
   ```

2. **Verify Tamil is available:**
   ```bash
   espeak-ng --voices | grep ta
   ```
   You should see: `ta    Madras         Tamil`

3. **Test Tamil speech:**
   ```bash
   espeak-ng -v ta "வணக்கம்" -s 150
   ```

4. **Update OfflineAI to use espeak-ng:**
   Edit `modules/voice_output.py` and add espeak support:

   ```python
   import subprocess
   import platform

   def speak_tamil_espeak(text):
       """Use espeak-ng for Tamil voice output"""
       try:
           if platform.system() == "Windows":
               # Use espeak-ng with Tamil voice
               subprocess.run([
                   "espeak-ng",
                   "-v", "ta_IN",  # Tamil India
                   "-s", "150",     # Speed
                   "-a", "200",     # Amplitude
                   text
               ], check=True)
           return True
       except Exception as e:
           print(f"[Error] espeak-ng failed: {e}")
           return False
   ```

### Option 4: Google Cloud Text-to-Speech (Internet Required, Not Fully Offline)
If you want high-quality Tamil voice, Google Cloud TTS has excellent Tamil support:
```bash
pip install google-cloud-texttospeech
```
However, this requires internet connection.

---

## Quick Test

After installing your chosen TTS engine, test with:

```bash
cd c:\Users\jayaprakash.k\OneDrive\Documents\Ai\OfflineAI
python -c "
from modules.voice_output import VoiceOutput
v = VoiceOutput()
v.speak('வணக்கம்')  # Should hear Tamil greeting
"
```

---

## Recommendation

For **fully offline, lightweight Tamil support**:
- **Install espeak-ng** (Option 3)
- It's free, offline, and supports 100+ languages including Tamil
- Update `voice_output.py` to use espeak-ng as fallback after pyttsx3

---

## Limitations

- **Speech Recognition**: Still English-only (Vosk model for Tamil not available)
- **Text Output**: Already in Tamil ✓
- **Voice Output**: Can be Tamil with espeak-ng or other TTS engines

Once you install a Tamil TTS engine, OfflineAI will provide **true bilingual experience** with Tamil input prompts, Tamil text responses, and Tamil audio output!
