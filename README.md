# Drishti — Offline Vision-Language Accessibility Assistant

**See it. Hear it. Understand it.** Fully offline, runs entirely on-device on Snapdragon.

Built for the Snapdragon® AI Lab Build & Present Challenge.

## Problem

Millions of visually impaired and low-literacy people in India struggle to independently read medicine labels, handwritten notes, signs, and forms. Existing accessibility readers (e.g. cloud-based screen readers) require a stable internet connection — a real barrier in rural areas, during travel, or simply when connectivity is unreliable. Drishti removes that dependency entirely.

## What it does

Point a camera at anything — a medicine label, a handwritten note, a sign — and Drishti:

1. **Reads and understands the image** using a Vision-Language Model (VLM) running on the Hexagon NPU
2. **Translates and simplifies** the result into the user's preferred Indian language using a second on-device LLM
3. **Speaks it aloud**

All inference happens **on-device**. No data ever leaves the machine. No internet connection required after the initial model download.

## Architecture

```
Camera / Image
      │
      ▼
┌─────────────────────────────┐
│  Vision Layer (GenieX)       │
│  Qwen3-VL-2B-Instruct-GGUF   │
│  runs on Hexagon NPU          │
└─────────────────────────────┘
      │  (English description / text read)
      ▼
┌─────────────────────────────┐
│  Language Layer (GenieX)      │
│  Qwen3.5-4B-GGUF               │
│  runs on Hexagon NPU           │
└─────────────────────────────┘
      │  (translated, simplified text)
      ▼
┌─────────────────────────────┐
│  Speech Layer (pyttsx3)        │
│  offline text-to-speech        │
└─────────────────────────────┘
      │
      ▼
   Spoken audio output
```

Both AI models run through **GenieX**, Qualcomm's on-device inference runtime, targeting the Hexagon NPU via the QAIRT/GGUF backend. The speech layer uses `pyttsx3` for fully offline, dependency-free text-to-speech.

## Why offline matters (not just a feature — the whole point)

| | Cloud-based readers | Drishti |
|---|---|---|
| Requires internet | Yes | **No** |
| Data leaves device | Yes | **No** |
| Works in low-connectivity areas | No | **Yes** |
| Subscription / API cost | Often | **None** |

## Setup

Requires **Windows ARM64** (Snapdragon device) or **Linux ARM64** — GenieX's SDK does not currently support x86/x64 platforms.

```bash
git clone https://github.com/Shashank4864/drishti-snapdragon.git
cd drishti-snapdragon
python -m venv venv
venv\Scripts\activate
pip install --only-binary=:all: numpy
pip install --only-binary=:all: qai-hub streamlit pillow requests pyttsx3
pip install geniex
streamlit run app.py
```

## Benchmark (verified on Snapdragon X2 Elite via Qualcomm Device Cloud)

Real end-to-end test: photograph of a pharmaceutical label → text extraction → Hindi translation.

| Stage | Model | Time |
|---|---|---|
| Vision (read image) | Qwen3-VL-2B-Instruct-GGUF | 19.05s |
| Translation (to Hindi) | Qwen3.5-4B-GGUF | 12.85s |
| **Total (offline, on-device)** | | **31.90s** |

Sample output (medicine label → Hindi):
> **Read:** "MEPERIDINE HCI INJECTION, USP... 50 mg/mL... WARNING: May be habit forming..."
> **Translated:** "मिपराइडिन इंजेक्शन (यूएसपी) क्लोराइड 50 mg/mL में प्रत्येक बॉटल में 2 mL होता है..."

Translation quality was also verified for Telugu after upgrading the language model from 2B to 4B parameters — the smaller model produced grammatically backwards output on casual sentences; the 4B model corrected this while still running fully on-device.

## Limitations & Roadmap

- **VLM occasionally hallucinates details on dense, technical labels.** For example, on a pharmaceutical label with small print, the model correctly read the core product name, strength, and primary warning, but invented some surrounding text not actually present. For any real deployment involving medical or safety-critical content, this would need an OCR verification layer or a larger/fine-tuned model before being trusted as-is. This is a known category of VLM failure (models "filling in" plausible text) and is flagged here deliberately rather than hidden.
- **Translation quality varies by language.** Hindi translation quality is strong. Other Indian languages (tested: Telugu) showed reduced fluency at smaller model sizes; a 4B-parameter model closed most of this gap. Further languages would need individual verification.
- **Model size vs. speed tradeoff.** Current model sizes (2B vision, 4B language) were chosen to balance on-device latency against quality. A larger model would likely reduce hallucination further at the cost of speed and download size.
- **Not yet tested:** broader real-world object coverage beyond labels and general scenes; sustained multi-turn conversation use.

## Tech Stack

- **GenieX** (Qualcomm) — on-device LLM/VLM inference runtime, Hexagon NPU
- **Qwen3-VL-2B-Instruct** — vision-language model
- **Qwen3.5-4B** — language/translation model
- **pyttsx3** — offline text-to-speech
- **Streamlit** — application UI
- **Qualcomm AI Hub** — model profiling and compilation
- **Qualcomm Device Cloud (QDC)** — remote Snapdragon hardware testing

## License

Built for the Snapdragon® AI Lab Build & Present Challenge. Intellectual property remains with the participant per challenge rules.
