from geniex import AutoModelForCausalLM

_model = None

LANG_MAP = {
    "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "English": "en"
}

def get_model():
    global _model
    if _model is None:
        _model = AutoModelForCausalLM.from_pretrained(
            "unsloth/Qwen3.5-2B-GGUF",
            precision="Q4_0"
        )
    return _model

def simplify_and_translate(raw_text: str, target_lang: str = "Hindi") -> str:
    model = get_model()
    messages = [{
        "role": "user",
        "content": (
            f"Rewrite the following for a low-literacy adult reader, in simple, "
            f"short sentences, translated into {target_lang}. Keep it under 3 sentences. "
            f"Do not add commentary, only the translated explanation.\n\n"
            f"Text: {raw_text}"
        )
    }]
    prompt = model.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    output = model.generate(prompt, max_new_tokens=200)
    return output.text.strip()