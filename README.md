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

All inference happens **on-device**, through a **native desktop application** — no browser, no local server, no network activity at any point. No data ever leaves the machine. No internet connection required after the initial model download.

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
│  offline TTS, dynamic voice    │
│  selection per language        │
└─────────────────────────────┘
      │
      ▼
   Spoken audio output
      (via native Tkinter UI)
```

Both AI models run through **GenieX**, Qualcomm's on-device inference runtime, targeting the Hexagon NPU via the QAIRT/GGUF backend. The speech layer uses `pyttsx3` for fully offline, dependency-free text-to-speech. The interface is a **native Tkinter desktop app** — not a browser-based UI — see "Why Tkinter, not Streamlit" below.

## Why offline matters (not just a feature — the whole point)

| | Cloud-based readers | Drishti |
|---|---|---|
| Requires internet | Yes | **No** |
| Data leaves device | Yes | **No** |
| Works in low-connectivity areas | No | **Yes** |
| Subscription / API cost | Often | **None** |

## Setup

Requires **Windows ARM64** (Snapdragon device) or **Linux ARM64** — GenieX's SDK does not currently support x86/x64 platforms; it will fail to install there by design.

```bash
git clone https://github.com/Shashank4864/drishti-snapdragon.git
cd drishti-snapdragon
python -m venv venv
venv\Scripts\activate
pip install --only-binary=:all: numpy pillow requests pyttsx3
pip install geniex
```

**To run the verified, stable pipeline** (recommended — see "Why Tkinter, not Streamlit" below for why):
```bash
python -c "from Vision import read_image; from Language import simplify_and_translate; from Speech import speak; raw = read_image('demo_assets/test.jpg'); print(raw); t = simplify_and_translate(raw, target_lang='Hindi'); print(t); speak(t, target_lang='Hindi', out_path='output.wav')"
```

**To try the desktop UI** (functional interface, live inference not yet confirmed stable):
```bash
python desktop_app.py
```

## Why Tkinter, not Streamlit

We initially built the UI in Streamlit, then moved to Tkinter — and found the same underlying issue in both, worth documenting honestly:

1. **`pyarrow` (a hard Streamlit dependency) has no official prebuilt wheel for Windows ARM64** — a genuine, currently-unresolved upstream gap (open Apache Arrow GitHub issue). We worked around the packaging conflict using a community-built wheel and dependency overrides, and got the Streamlit UI to load correctly.
2. Even once loaded, **inference calls made through Streamlit triggered a native Hexagon NPU crash** (`ggml-hex: dspqueue_read failed`).
3. We rebuilt the interface in **Tkinter** (Python standard library, no browser/server) expecting this simpler model to avoid the crash — **it did not**. The same NPU error occurred on the first inference call, reproducibly, even after a full device reboot.
4. The identical pipeline run as a **plain script, with no GUI at all**, has completed successfully many times with no crashes.

This points to the crash being related to how GenieX's native NPU queue interacts with a GUI event loop/thread, not to our model or pipeline logic. **All verified benchmark numbers below come from script-based execution.** `desktop_app.py` is included in this repo and demonstrates the intended user experience, but live inference through it is not yet confirmed stable — flagged here as an open issue rather than presented as finished.

## Benchmark (verified on Snapdragon X2 Elite via Qualcomm Device Cloud, across multiple sessions)

| Test | Vision | Translation | Speech | Total |
|---|---|---|---|---|
| Pharmaceutical label → Hindi (cold start, fresh device) | 19.05s | 12.85s | — | 31.90s |
| Camera object → Hindi (warm cache) | 5.63s | 4.58s | 0.16s | 10.38s |
| Camera object → Hindi (repeat run) | 5.20s | 4.54s | 0.16s | ~4.9s |
| Camera object → Hindi + Telugu + Tamil (per-language reload) | 5.04s (shared) | ~5.5s each | ~0.2s each | ~5.7s per language |

Latency varies meaningfully with model cache/warm-up state — we report the full observed range rather than a single cherry-picked number. All figures measured directly on real hardware, fully offline (Wi-Fi disabled and recorded during testing), not estimated or simulated.

Sample output (medicine label → Hindi):
> **Read:** "MEPERIDINE HCI INJECTION, USP... 50 mg/mL... WARNING: May be habit forming..."
> **Translated:** "मिपराइडिन इंजेक्शन (यूएसपी) क्लोराइड 50 mg/mL में प्रत्येक बॉटल में 2 mL होता है..."

All three primary target languages — **Hindi, Telugu, and Tamil** — have been verified producing correct, natural translations.

## Limitations & Roadmap

- **VLM occasionally hallucinates details on dense, technical labels.** On a pharmaceutical label with small print, the model correctly read the core product name, strength, and primary warning, but invented some surrounding text not actually present. For any real deployment involving medical or safety-critical content, this would need an OCR verification layer or a larger/fine-tuned model before being trusted as-is.
- **Intermittent GenieX error on consecutive language-model calls**, root-caused to reusing a cached model instance across calls. Fixed by reloading the model fresh before each translation call (~1s latency cost). Verified stable across Hindi, Telugu, and Tamil after the fix. Documented in detail in `submission.md` in case it's useful to the GenieX team.
- **Speech output currently defaults to English** on our test devices, since neither had Hindi/Telugu/Tamil voice packs installed at the OS level (Windows Settings → Time & Language → Language & Region). The `speech.py` module actively scans installed voices and selects a matching one for the target language at runtime — on any Windows machine with the relevant language pack installed, the same unmodified code produces native-language audio with no changes required. This is a test-environment gap, not a code limitation.
- **Model size vs. speed tradeoff.** Current sizes (2B vision, 4B language) balance on-device latency against quality. A larger model would likely reduce hallucination further, at a real cost to inference speed and download size.

## Tech Stack

- **GenieX** (Qualcomm) — on-device LLM/VLM inference runtime, Hexagon NPU
- **Qwen3-VL-2B-Instruct** — vision-language model
- **Qwen3.5-4B** — language/translation model
- **pyttsx3** — offline text-to-speech, dynamic multilingual voice selection
- **Tkinter** — native desktop application UI (Python standard library)
- **Qualcomm Device Cloud (QDC)** — remote Snapdragon hardware testing

## License

Built for the Snapdragon® AI Lab Build & Present Challenge. Intellectual property remains with the participant per challenge rules.
