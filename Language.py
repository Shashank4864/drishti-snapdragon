from geniex import AutoModelForCausalLM

LANG_MAP = {
    "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "English": "en"
}

def simplify_and_translate(raw_text: str, target_lang: str = "Hindi") -> str:
    model = AutoModelForCausalLM.from_pretrained(
        "unsloth/Qwen3.5-4B-GGUF",
        precision="Q4_0"
    )
    try:
        messages = [{
            "role": "user",
            "content": (
                f"Translate this English text into {target_lang} in one simple sentence. "
                f"Output ONLY the translation, nothing else.\n\n"
                f"Text: {raw_text}"
            )
        }]
        prompt = model.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        output = model.generate(
            prompt,
            max_new_tokens=100,
            temperature=0.3,
            repetition_penalty=1.3
        )
        return output.text.strip()
    finally:
        model.close()