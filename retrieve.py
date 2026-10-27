"""Retrieval over the curated condition reference.

Two access paths: exact lookup by the label SkinSense predicts, and TF-IDF
search for free-text follow-up questions. Six entries do not justify a vector
database; TF-IDF over the same documents is the same idea without the infra.
"""
import json
import pathlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_DATA = pathlib.Path(__file__).parent / "data" / "conditions.json"
CONDITIONS = json.loads(_DATA.read_text())


def entry_text(entry):
    return " ".join([
        entry["name"], entry["what_it_is"], entry["typical_appearance"],
        entry["who_gets_it"], entry["when_to_see_a_clinician"],
    ])


_KEYS = list(CONDITIONS)
_DOCS = [entry_text(CONDITIONS[k]) for k in _KEYS]
_VEC = TfidfVectorizer(stop_words="english").fit(_DOCS)
_M = _VEC.transform(_DOCS)


def by_label(label):
    """Exact lookup on the classifier's label. Returns None if unknown."""
    return CONDITIONS.get(label.strip().lower().replace(" ", "_"))


def search(question, k=2, floor=0.05):
    """TF-IDF search for follow-up questions. Returns [] when nothing is close
    enough, which the caller must treat as 'refuse to answer' rather than
    falling back to the model's own memory."""
    sims = cosine_similarity(_VEC.transform([question]), _M)[0]
    ranked = sorted(zip(_KEYS, sims), key=lambda p: -p[1])
    return [(k_, CONDITIONS[k_], float(s)) for k_, s in ranked[:k] if s > floor]
