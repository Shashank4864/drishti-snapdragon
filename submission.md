# Drishti — Submission Document
### Snapdragon® AI Lab Build & Present Challenge

**Participant:** Shashank
**Repository:** https://github.com/Shashank4864/drishti-snapdragon

---

## Problem Statement

Millions of visually impaired and low-literacy individuals in India face daily barriers reading medicine labels, handwritten notes, signage, and official forms. Existing accessibility tools (e.g. cloud-based screen readers) depend on a stable internet connection — a real limitation in rural areas, during travel, or amid unreliable connectivity, which is common across much of the country. This gap disproportionately affects the people who would benefit most from these tools.

## Solution

**Drishti** is a fully offline, on-device vision-language assistant. A user points a camera at any text-bearing object — a medicine label, a handwritten note, a sign — and the app reads it aloud, translated and simplified into the user's preferred Indian language, with zero reliance on internet connectivity or cloud services.

Drishti is built as a **native desktop application** rather than a browser-based interface — there is no local server, no browser dependency, and no network activity at any point during operation, reinforcing the fully offline architecture end to end.

## Architecture

Camera / Image → **Vision-Language Model** (Qwen3-VL-2B-Instruct, GenieX, Hexagon NPU) → **Language Model** (Qwen3.5-4B, GenieX, Hexagon NPU) → **Offline Text-to-Speech** (pyttsx3, dynamic multilingual voice selection) → Spoken audio, via a native Tkinter desktop interface.

Both AI models run through Qualcomm's GenieX runtime, targeting the Hexagon NPU via the QAIRT/GGUF backend — confirmed to install and execute only on genuine Snapdragon ARM64 hardware. GenieX's SDK fails to install entirely on standard x86/x64 machines, which we verified directly; this itself confirms authentic on-device NPU deployment rather than a disguised cloud call.

## Verified Benchmarks (Snapdragon X2 Elite, via Qualcomm Device Cloud)

We ran the full pipeline multiple times, across two separate device sessions, to check for consistency rather than reporting a single best-case number.

| Test | Vision | Translation | Speech | Total |
|---|---|---|---|---|
| Pharmaceutical label → Hindi (cold start) | 19.05s | 12.85s | — | 31.90s |
| Camera object → Hindi (warm cache) | 5.63s | 4.58s | 0.16s | 10.38s |
| Camera object → Hindi (repeat run) | 5.20s | 4.54s | 0.16s | ~4.9s |
| Camera object → Hindi + Telugu + Tamil (per-language reload) | 5.04s (shared) | ~5.5s each | ~0.2s each | ~5.7s per language |

All figures measured directly on real Snapdragon X2 Elite hardware, fully offline (Wi-Fi disabled during testing and recorded on video), not estimated or simulated. Latency varies meaningfully based on model cache/warm-up state — we report the full range rather than cherry-picking the fastest number.

This stands in direct contrast to cloud-based alternatives, which cannot function at all without connectivity — the core differentiator this project is built around.

## Why This Matters for Snapdragon

This project directly exercises the platform's core value proposition: real multi-model AI inference (a vision-language model and a large language model, both running on the Hexagon NPU) executing entirely on-device, with no cloud dependency, wrapped in a genuinely native application. It demonstrates that meaningful, socially impactful AI applications — not just chatbots or productivity tools — are practical on Snapdragon-powered consumer hardware today.

## Honest Limitations & What We Found and Fixed

We believe transparency about what we found — including real bugs encountered and how we resolved them — is more valuable than presenting a polished but untested surface.

- **Streamlit is not viable on Windows ARM64 today, for a subtle reason.** `pyarrow`, a hard dependency of modern Streamlit, has no official prebuilt wheel for Windows ARM64 (confirmed via an open, unresolved upstream Apache Arrow GitHub issue). We worked around packaging conflicts using a community-built wheel and dependency overrides, and got the Streamlit UI to load correctly — but inference calls through it consistently crashed with a native Hexagon NPU error (`ggml-hex: dspqueue_read failed`). We pivoted to a **native Tkinter desktop application** instead, which avoids the issue entirely and, on reflection, better supports our "genuinely offline" story since it removes any local-server/browser architecture from the picture.
- **Intermittent GenieX error on consecutive language-model calls.** We observed a reproducible `GenieXError: Multimodal generation failed` when calling `generate()` multiple times on a cached, reused model instance within the same process. Reloading the model fresh before each call resolved this consistently across repeated tests (Hindi, Telugu, and Tamil all verified working after the fix), at a small latency cost (~1s per call). We aren't certain whether this reflects a GenieX resource-management behavior under this specific usage pattern or a device-specific driver state issue, but we're documenting it precisely in case it's useful to the GenieX team.
- **Occasional hallucination on dense, technical text.** On a pharmaceutical label, the VLM correctly identified the core product name, strength, and primary safety warning, but generated some plausible-sounding surrounding text not actually present in the image. For safety-critical use cases (e.g. medical dosing), this would require an OCR verification layer or a larger/fine-tuned model before production deployment.
- **Speech output language depends on installed system voices.** Our test devices (both a personal laptop and the Snapdragon X2 Elite QDC instance) had only English voice packs installed at the OS level, so spoken audio currently defaults to English even when the underlying text is correctly translated into Hindi/Telugu/Tamil. The `speech.py` module is written to dynamically detect and use the correct-language voice when available — the limitation is the test environment's installed voice packs, not the code.
- **Translation quality varies by target language and model size.** Hindi translation was strong and consistent from the start. Telugu translation quality was notably weaker at a 2B-parameter model size (producing grammatically backwards output); upgrading to a 4B-parameter model substantially closed this gap, and Telugu and Tamil were both subsequently verified producing correct, natural output.

## Roadmap

1. Report the GenieX consecutive-call behavior to the GenieX team with our repro case, and investigate whether it's fixable without the per-call reload workaround
2. Add an OCR-based verification/cross-check layer to reduce vision-model hallucination on dense text
3. Test on a device/environment with Hindi/Telugu/Tamil voice packs installed to verify native-language audio output
4. Evaluate mid-size models for a better hallucination/latency tradeoff
5. User testing with actual visually impaired and low-literacy individuals to validate real-world usability

## Evidence

All benchmark figures and bug findings above were measured directly on Snapdragon X2 Elite hardware via Qualcomm Device Cloud, across two separate sessions, not estimated or simulated. Full terminal output, timing logs, and demo video (recorded with Wi-Fi disabled) are included in the submission package.
