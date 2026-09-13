# Drishti — Submission Document
### Snapdragon® AI Lab Build & Present Challenge

**Participant:** Shashank
**Repository:** https://github.com/Shashank4864/drishti-snapdragon

---

## Problem Statement

Millions of visually impaired and low-literacy individuals in India face daily barriers reading medicine labels, handwritten notes, signage, and official forms. Existing accessibility tools (e.g. cloud-based screen readers) depend on a stable internet connection — a real limitation in rural areas, during travel, or amid unreliable connectivity, which is common across much of the country. This gap disproportionately affects the people who would benefit most from these tools.

## Solution

**Drishti** is a fully offline, on-device vision-language assistant. A user points a camera at any text-bearing object — a medicine label, a handwritten note, a sign — and the app reads it aloud, translated and simplified into the user's preferred Indian language, with zero reliance on internet connectivity or cloud services.

## Architecture

Camera → **Vision-Language Model** (Qwen3-VL-2B, GenieX, Hexagon NPU) → **Language Model** (Qwen3.5-4B, GenieX, Hexagon NPU) → **Offline Text-to-Speech** (pyttsx3) → Spoken audio.

Both AI models run through Qualcomm's GenieX runtime, targeting the Hexagon NPU via the QAIRT/GGUF backend — confirmed to install and execute only on genuine Snapdragon ARM64 hardware (verified: it does not install at all on standard x86/x64 machines, which itself confirms authentic on-device NPU deployment rather than a disguised cloud call).

## Verified Benchmark (Snapdragon X2 Elite, via Qualcomm Device Cloud)

Real end-to-end test — photograph of a pharmaceutical label, processed fully offline:

| Stage | Model | Time |
|---|---|---|
| Vision (image → text) | Qwen3-VL-2B-Instruct | 19.05s |
| Translation (English → Hindi) | Qwen3.5-4B | 12.85s |
| **Total, fully offline** | | **31.90s** |

This stands in direct contrast to cloud-based alternatives, which cannot function at all without connectivity — the core differentiator this project is built around.

## Why This Matters for Snapdragon

This project directly exercises the platform's core value proposition: real multi-model AI inference (a vision-language model and a large language model running concurrently) executing entirely on the Hexagon NPU, with no cloud dependency. It demonstrates that meaningful, socially impactful AI applications — not just chatbots or productivity tools — are practical on Snapdragon-powered consumer hardware today.

## Honest Limitations

We believe transparency about current limitations is more valuable than overstating readiness:

- **Occasional hallucination on dense, technical text.** On a pharmaceutical label, the VLM correctly identified the core product name, strength, and primary safety warning, but generated some plausible-sounding surrounding text not actually present in the image. For safety-critical use cases (e.g. medical dosing), this would require an OCR verification layer or a larger/fine-tuned model before production deployment.
- **Translation quality varies by target language.** Hindi translation was strong and consistent. Telugu translation quality was notably weaker at a 2B-parameter model size (producing grammatically backwards output); upgrading to a 4B-parameter model substantially closed this gap while still running fully on-device. Further Indian languages would need individual verification before being claimed as supported.
- **Model size is a deliberate speed/accuracy tradeoff.** Current sizes (2B vision, 4B language) were chosen to keep on-device latency reasonable. Larger models would likely reduce hallucination further, at a real cost to inference speed and initial download size.

## Roadmap

1. Add an OCR-based verification/cross-check layer to reduce hallucination on dense text
2. Expand and individually verify support for additional Indian languages
3. Evaluate mid-size models (e.g. 3B–4B vision-language) for a better hallucination/latency tradeoff
4. User testing with actual visually impaired and low-literacy individuals to validate real-world usability

## Evidence

All benchmark figures above were measured directly on Snapdragon X2 Elite hardware via Qualcomm Device Cloud, not estimated or simulated. Full terminal output, timing logs, and demo video are included in the submission package.
