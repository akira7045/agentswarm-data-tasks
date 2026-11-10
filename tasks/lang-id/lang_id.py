"""Train from the supplied synthetic titles and detect one ISO 639-1 code.

Character n-gram language identification with a smoothed multinomial naive-Bayes
model. Each training title is normalized (NFKC, casefold, whitespace collapse,
punctuation removal) and expanded into character n-grams of several lengths.
Per-language n-gram likelihoods are learned from the supplied JSON file only.
A title is classified by its average log-likelihood under each language model
(length-normalized so long titles are not favored) plus the language log-prior.
An unobserved n-gram gets one shared fallback probability (not per-language),
which keeps predictions from collapsing toward the language with the smallest
n-gram vocabulary on unknown text. No external corpora, word tables or script
routing are used.
"""
from collections import Counter, defaultdict
import json
import math
import os
import unicodedata

_NGRAM_SIZES = (2, 3, 4)
_ALPHA = 0.1


def _train_path():
    env = os.environ.get("LANG_ID_TRAIN")
    if env:
        return env
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "fixtures", "train.json")


def _normalize(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.casefold()
    text = "".join(ch for ch in text if ch.isspace() or not unicodedata.category(ch).startswith("P"))
    text = " ".join(text.split())
    return text.strip("!?.")


def _ngrams(text):
    grams = []
    for n in _NGRAM_SIZES:
        for i in range(len(text) - n + 1):
            grams.append(text[i:i + n])
    return grams


def _load_model():
    with open(_train_path(), "r", encoding="utf-8") as handle:
        rows = json.load(handle)
    counts = defaultdict(Counter)
    docs = Counter()
    for row in rows:
        language = row["language"]
        docs[language] += 1
        counts[language].update(_ngrams(_normalize(row["text"])))
    languages = sorted(counts)
    total_docs = sum(docs.values())
    global_vocab = set()
    for counter in counts.values():
        global_vocab.update(counter)
    seen_types = len(global_vocab)
    total_tokens = sum(sum(c.values()) for c in counts.values())
    log_unseen = math.log(_ALPHA / (total_tokens + _ALPHA * (seen_types + 1)))
    models = {}
    for language in languages:
        counter = counts[language]
        total = sum(counter.values())
        vocab = len(counter)
        denom = total + _ALPHA * (vocab + 1)
        log_prior = math.log(docs[language] / total_docs)
        models[language] = (counter, denom, log_prior, log_unseen)
    return languages, models


_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        _MODEL = _load_model()
    return _MODEL


def detect(text):
    normalized = _normalize(text)
    if not normalized:
        return "en"
    languages, models = _model()
    grams = _ngrams(normalized)
    best_language = "en"
    best_score = None
    for language in languages:
        counter, denom, log_prior, log_unseen = models[language]
        total_log = log_prior
        count = 0
        for gram in grams:
            count += 1
            c = counter.get(gram)
            if c:
                total_log += math.log((c + _ALPHA) / denom)
            else:
                total_log += log_unseen
        score = total_log / count if count else log_prior - 1e9
        if best_score is None or score > best_score:
            best_score = score
            best_language = language
    return best_language
