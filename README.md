---
title: SkinSense Explainer
emoji: 🩺
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
---

# SkinSense Explainer

A plain-language explanation layer over [SkinSense](https://huggingface.co/spaces/Elisha622/skinsense),
my skin-condition image classifier. The classifier returns a label and a confidence
score; this service turns that into something a patient can actually read, without
letting the language model invent anything or give medical advice.

## Pipeline

1. **Retrieve** — the predicted label is looked up in a curated reference
   (`data/conditions.json`). Free-text follow-up questions go through TF-IDF
   search over the same entries.
2. **Generate** — an LLM rewrites the retrieved entry in plain English. The system
   prompt restricts it to the supplied reference text only.
3. **Validate** — every response is checked before display for treatment advice,
   definitive diagnostic claims, length, and whether each sentence is lexically
   grounded in the retrieved source.
4. **Fall back** — if validation fails, or no API key is set, or the call errors,
   the app serves deterministic text assembled from the reference entry. It
   degrades to something correct rather than to an error page.

## Design notes

**Why no vector database.** The reference set is six entries. TF-IDF over the same
documents gives the same retrieval behaviour with no additional infrastructure.
If the reference grows past a few dozen entries, swapping in embeddings is a
contained change inside `retrieve.py`.

**Why the cache is keyed on a confidence band.** Confidence arrives as a float, so
0.811 and 0.812 would be distinct cache keys and each would pay for its own API
call despite producing identical output. `llm.band()` buckets the score into
high/moderate/low first.

**Why grounding is checked lexically.** Sentence-level vocabulary overlap with the
source is a blunt proxy for hallucination, but it reliably catches the model
inventing whole statements. It is marked as a shortcut in `guard.py`; an
entailment model would be the upgrade if the reference set grows.

**A bug the tests caught.** The deterministic fallback initially failed its own
validation. Its framing sentences ("the image most closely resembles…") are the
app's own copy, not the reference entry's, so the grounding check flagged them as
ungrounded. Fixed by validating against the retrieved entry plus a constant of
app framing vocabulary — see `FRAMING` in `guard.py`.

## Safety

This is a triage aid, not a diagnostic tool. The validator blocks treatment advice
and definitive diagnostic claims, and every response carries a disclaimer. Questions
outside the reference set are refused rather than answered from model memory.

## Run it

```bash
pip install -r requirements.txt
python test_guard.py          # 12 checks on the validation layer
export LLM_API_KEY=...        # Groq free tier; OpenAI-compatible
python app.py
```

Without `LLM_API_KEY` the app still runs and serves the deterministic fallback.

| Variable | Default | Purpose |
|---|---|---|
| `LLM_API_KEY` | *(unset)* | API key; unset means fallback-only |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Any OpenAI-compatible endpoint |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model name |
