"""LLM client with caching.

Groq's free tier is OpenAI-compatible, so one client covers Groq, OpenAI and
anything else speaking the same protocol - switch with two env vars.
The cache matters: the same condition is explained over and over, and each
repeat would otherwise be a paid round trip for identical output.
"""
import os
from functools import lru_cache
from openai import OpenAI

BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
API_KEY = os.environ.get("LLM_API_KEY", "")

SYSTEM = """You explain skin-condition information to a patient in plain English.

Rules you must follow:
- Use ONLY the reference text supplied in the user message. If it does not
  cover something, say the reference does not cover it.
- Never give treatment advice, dosages, or product names.
- Never state the person has a condition. The image model reports a likeness
  and a confidence, nothing more.
- Three short paragraphs maximum. No lists, no headings, no markdown.
- Plain, calm language. No reassurance you cannot support."""


def _client():
    if not API_KEY:
        return None
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


@lru_cache(maxsize=256)
def explain(condition_name, confidence_band, reference, question=""):
    """Returns generated text, or None when no key is configured or the call fails.

    confidence_band is bucketed by the caller (not the raw float) so that
    near-identical scores share one cache entry instead of each paying for a call.
    """
    client = _client()
    if client is None:
        return None
    ask = question or "Explain what this condition is and when to seek advice."
    try:
        r = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            max_tokens=320,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Image model result: {condition_name}, {confidence_band} confidence.\n\n"
                    f"Reference text:\n{reference}\n\nTask: {ask}"},
            ],
        )
        return r.choices[0].message.content.strip()
    except Exception as e:                      # noqa: BLE001 - degrade, never crash the UI
        print(f"[llm] call failed, using fallback: {type(e).__name__}: {e}")
        return None


def band(confidence):
    """Bucket a raw score so the cache is not defeated by 0.811 vs 0.812."""
    if confidence >= 0.85:
        return "high"
    if confidence >= 0.60:
        return "moderate"
    return "low"
