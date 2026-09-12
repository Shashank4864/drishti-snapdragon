import geniex

geniex.init()

VLM_MODEL = "ai-hub-models/Qwen2.5-VL-7B-Instruct"

def read_image(image_path: str, instruction: str = None) -> str:
    prompt = instruction or (
        "You are helping a visually impaired or low-literacy person. "
        "Describe exactly what this image shows and read any visible text "
        "word for word. Be clear and literal."
    )
    result = geniex.infer(
        model=VLM_MODEL,
        images=[image_path],
        prompt=prompt,
    )
    return result.text.strip()