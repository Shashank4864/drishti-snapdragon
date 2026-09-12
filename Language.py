import geniex

LLM_MODEL = "google/gemma-3-4b-it-qat-q4_0-gguf"

LANG_MAP = {
    "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "English": "en"
}

def simplify_and_translate(raw_text: str, target_lang: str = "Hindi") -> str:
    prompt = (
        f"Rewrite the following for a low-literacy adult reader, in simple, "
        f"short sentences, translated into {target_lang}. Keep it under 3 sentences. "
        f"Do not add commentary, only the translated explanation.\n\n"
        f"Text: {raw_text}"
    )
    result = geniex.infer(model=LLM_MODEL, prompt=prompt)
    return result.text.strip()