"""Normalize CSV headers into unique, offline-safe field names.

Self-contained, Python 3.11+ standard library only. No network, files, clock
or CSV reading. See SPEC.md for the full contract.
"""
import unicodedata

_ASCII_LOWER = frozenset("abcdefghijklmnopqrstuvwxyz")
_ASCII_DIGITS = frozenset("0123456789")
_FALLBACK = "column"


def _normalize_one(header):
    """NFKC -> casefold, collapse maximal non-[a-z0-9] runs to "_", strip."""
    text = unicodedata.normalize("NFKC", header).casefold()
    parts = []
    in_run = False
    for ch in text:
        if ch in _ASCII_LOWER or ch in _ASCII_DIGITS:
            parts.append(ch)
            in_run = False
        elif not in_run:
            parts.append("_")
            in_run = True
    name = "".join(parts).strip("_")
    return name if name else _FALLBACK


def normalize_headers(headers):
    """Return a fresh list of unique, normalized field names.

    Raises TypeError if ``headers`` is not an exact ``list`` or any element is
    not an exact ``str``. The input is never mutated.
    """
    if type(headers) is not list:
        raise TypeError("headers must be a list")
    for item in headers:
        if type(item) is not str:
            raise TypeError("every header must be a str")

    used = set()
    result = []
    for header in headers:
        base = _normalize_one(header)
        name = base
        counter = 2
        while name in used:
            name = "%s_%d" % (base, counter)
            counter += 1
        used.add(name)
        result.append(name)
    return result
