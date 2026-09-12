import streamlit as st
from PIL import Image
import tempfile, time

from vision import read_image
from language import simplify_and_translate, LANG_MAP
from speech import speak

st.set_page_config(page_title="Drishti", page_icon="👁️")
st.title("👁️ Drishti — See it. Hear it. Understand it.")
st.caption("Fully offline · Runs entirely on-device · No internet required")

lang = st.selectbox("Choose language", list(LANG_MAP.keys()))

col1, col2 = st.columns(2)
with col1:
    camera_img = st.camera_input("Use camera")
with col2:
    uploaded_img = st.file_uploader("Or upload image", type=["jpg", "jpeg", "png"])

img_file = camera_img or uploaded_img

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Captured", width=300)

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name)
        img_path = f.name

    t0 = time.time()
    with st.spinner("Reading image..."):
        raw_description = read_image(img_path)
    t1 = time.time()

    with st.spinner(f"Translating to {lang}..."):
        final_text = simplify_and_translate(raw_description, target_lang=lang)
    t2 = time.time()

    with st.spinner("Generating speech..."):
        audio_path = speak(final_text, lang_code=LANG_MAP[lang])
    t3 = time.time()

    st.success(final_text)
    st.audio(audio_path)

    st.caption(
        f"⏱️ Vision: {t1-t0:.2f}s | Translation: {t2-t1:.2f}s | "
        f"Speech: {t3-t2:.2f}s | Total: {t3-t0:.2f}s — all on-device, offline"
    )