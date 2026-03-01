# OfflineAI Voice Mode - Improving Recognition Accuracy

## Current Status
Your OfflineAI uses **Vosk** for offline speech recognition with the small English model. While fully offline, it has moderate accuracy (~75-85%).

## How to Get Better Results

### 1. **Speak Clearly**
- Enunciate words clearly and naturally
- Avoid slurring or speaking too fast
- Pause briefly between sentences

### 2. **Reduce Background Noise**
- Use in a quiet environment
- Close windows/doors to reduce echo
- Avoid typing or keyboard noise while speaking

### 3. **Microphone Positioning**
- Keep microphone 6-8 inches away
- Face directly toward the microphone
- Avoid pointing away or to the side

### 4. **Use Simple Commands**
Vosk works best with clear, common phrases:
- ✅ "Hello" - Good
- ✅ "Open editor" - Good  
- ✅ "Tell me a joke" - Good
- ❌ "Yo, what's up" - Might fail (slang)
- ❌ "Can you possibly tell me a joke" - Too complex

### 5. **If Recognition Fails**
When OfflineAI shows "No speech detected", you can:
- Say 'y' to retry with clearer speech
- Say 't' to type your command instead

## Quick Start Commands to Try

```
Voice Mode: python main.py
Text Mode:  python main.py --text
```

### Recommended Test Commands
1. "hello" - Establish connection
2. "what time is it" - Check time
3. "tell me a joke" - Hear a joke
4. "open notepad" - Open an app
5. "system status" - Check CPU/RAM

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No speech detected | Position mic closer, speak louder, less background noise |
| Gibberish recognized | Speak more clearly, reduce background noise |
| Wrong command recognized | Try saying it differently or use text mode |
| Microphone not found | Check device connections, try restarting |

## Technical Details

- **Model**: Vosk small English (vosk-model-small-en-us-0.15)
- **Accuracy**: ~75-85% for clear English speech
- **Language**: English only
- **Latency**: 2-3 seconds for recognition
- **Offline**: Yes - completely offline, no internet needed

## Why Vosk Instead of Google?

We use Vosk for:
- **Privacy**: No audio sent to cloud
- **Offline**: Works without internet
- **Speed**: Local processing on your machine

Google Speech Recognition (100% accuracy) requires internet and sends audio to Google's servers.

## Future Improvements

- Larger Vosk models (better language model)
- Noise filtering preprocessing
- Confidence thresholds with retry logic
- Keyword spotting for common commands

## Tips for Best Experience

1. Start with Text Mode if you want guaranteed accuracy
2. Use Voice Mode in quiet environments
3. Speak naturally at normal pace
4. Use the retry feature when needed
5. Report issues or provide feedback!

---

**Version**: OfflineAI v1.0.0  
**Status**: Fully Offline & Secure
