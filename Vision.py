from geniex import AutoModelForCausalLM

_model = None

def get_model():
    global _model
    if _model is None:
        _model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-VL-2B-Instruct-GGUF",
            device_map="auto"
        )
    return _model

def read_image(image_path: str, instruction: str = None) -> str:
    model = get_model()
    prompt_text = instruction or (
        "You are helping a visually impaired or low-literacy person. "
        "Describe exactly what this image shows and read any visible text "
        "word for word. Be clear and literal."
    )
    messages = [{
        "role": "user",
        "content": [
            {"type": "image", "image": image_path},
            {"type": "text", "text": prompt_text},
        ],
    }]
    prompt = model.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    output = model.generate(prompt, images=[image_path])
    return output.text.strip()