"""Output validation for LLM-generated patient explanations.

Two failure modes matter here and neither is caught by the model itself:
the model giving treatment advice, and the model stating something that is
not in the retrieved source. Both are checked before anything reaches a user.
"""
import re

# Prescriptive language. The app explains; it must never instruct.
TREATMENT_PATTERNS = [
    r"\byou should (take|apply|use|try|start|stop)\b",
    r"\b(take|apply|use) (this|these|a|an|the) (cream|tablet|steroid|antibiotic|antifungal|antihistamine)",
    r"\b\d+\s?(mg|ml)\b",
    r"\btwice (a|per) day\b|\bonce (a|per) day\b",
    r"\bI (recommend|suggest|advise)\b",
    r"\bprescrib",
]

# Definitive diagnostic claims. The classifier returns a likeness, not a verdict.
DIAGNOSIS_PATTERNS = [
    r"\byou (have|are suffering from|definitely have)\b",
    r"\bthis is (definitely|certainly|clearly)\b",
    r"\bdiagnos(is|ed) (is|as)\b",
    r"\bconfirms?\b",
]

MAX_CHARS = 1200

# The app's own fixed framing. These words are legitimately ours, not the
# reference entry's, so the grounding check must not treat them as invented.
FRAMING = (
    "the image most closely resembles confidence from model automated likeness "
    "check not a diagnosis what it usually looks like when to see a clinician "
    "based on reference information percent"
)
STOPWORDS = {
    "the","a","an","and","or","but","if","of","to","in","on","is","are","was","were",
    "it","its","this","that","these","those","with","as","for","your","you","can","may",
    "be","been","has","have","not","from","at","by","which","there","their","they","also",
}


def _words(text):
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOPWORDS}


def find_violations(text):
    """Return a list of reasons the text must not be shown. Empty list means it passed."""
    problems = []
    low = text.lower()
    for pat in TREATMENT_PATTERNS:
        if re.search(pat, low):
            problems.append(f"treatment advice matched /{pat}/")
            break
    for pat in DIAGNOSIS_PATTERNS:
        if re.search(pat, low):
            problems.append(f"definitive diagnosis matched /{pat}/")
            break
    if len(text) > MAX_CHARS:
        problems.append(f"too long ({len(text)} > {MAX_CHARS})")
    if not text.strip():
        problems.append("empty response")
    return problems


def ungrounded_sentences(text, source, min_overlap=0.30):
    """Sentences whose vocabulary barely overlaps the retrieved source.

    A blunt proxy for hallucination, but it reliably catches the model inventing
    whole statements that have no basis in the reference entry.
    shortcut: lexical overlap only, no entailment model; upgrade to an NLI check
    if the reference set grows past a few dozen entries.
    """
    src = _words(source)
    if not src:
        return []
    loose = []
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        sw = _words(sentence)
        if len(sw) < 4:
            continue
        if len(sw & src) / len(sw) < min_overlap:
            loose.append(sentence.strip())
    return loose


def validate(text, source):
    """(ok, reasons). ok is False if the text must be replaced by the fallback.

    Grounding is checked against the retrieved entry plus the app's own framing
    copy; without the latter the deterministic fallback fails its own check.
    """
    reasons = find_violations(text)
    loose = ungrounded_sentences(text, source + " " + FRAMING)
    if loose:
        reasons.append(f"{len(loose)} sentence(s) not grounded in source: {loose[0][:60]!r}")
    return (not reasons), reasons


def fallback(entry, confidence):
    """Deterministic text assembled straight from the reference entry.

    Used whenever the model output fails validation or the API is unavailable,
    so the app degrades to something correct rather than to an error.
    """
    return (
        f"The image most closely resembles {entry['name']} "
        f"({confidence:.0%} confidence from the image model).\n\n"
        f"{entry['what_it_is']}\n\n"
        f"What it usually looks like: {entry['typical_appearance']}\n\n"
        f"When to see a clinician: {entry['when_to_see_a_clinician']}\n\n"
        "This is an automated likeness check, not a diagnosis."
    )
