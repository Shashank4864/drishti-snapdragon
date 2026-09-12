import pyttsx3

def speak(text: str, lang_code: str = "hi", out_path: str = "output.wav") -> str:
    engine = pyttsx3.init()
    engine.save_to_file(text, out_path)
    engine.runAndWait()
    return out_path