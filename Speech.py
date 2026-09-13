import pyttsx3

# Maps our app's language names to voice-matching keywords
LANG_VOICE_HINTS = {
    "Hindi": ["hindi", "hi-in", "hi_in"],
    "Telugu": ["telugu", "te-in", "te_in"],
    "Tamil": ["tamil", "ta-in", "ta_in"],
    "English": ["english", "en-us", "en_us", "en-in", "en_in"],
}

def speak(text: str, target_lang: str = "English", out_path: str = "output.wav") -> str:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    hints = LANG_VOICE_HINTS.get(target_lang, [])
    matched_voice = None

    for v in voices:
        voice_id = str(v.id).lower()
        voice_name = str(v.name).lower()
        voice_langs = [str(l).lower() for l in (v.languages or [])]

        for hint in hints:
            if hint in voice_id or hint in voice_name or any(hint in vl for vl in voice_langs):
                matched_voice = v.id
                break
        if matched_voice:
            break

    if matched_voice:
        engine.setProperty('voice', matched_voice)
    else:
        print(f"[speech.py] No installed voice found for '{target_lang}' — using default system voice.")

    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path