"""Normalize an authored task title offline; see SPEC.md."""
import unicodedata


def _validate(text, max_length):
    if type(text) is not str:
        raise TypeError('text must be str')
    if type(max_length) is not int:
        raise TypeError('max_length must be int')
    if not 1 <= max_length <= 128:
        raise ValueError('max_length out of range')


def normalize_slug(text, max_length=64):
    _validate(text, max_length)

    decomposed = unicodedata.normalize('NFKD', text.casefold())
    stripped = ''.join(
        ch for ch in decomposed
        if not unicodedata.category(ch).startswith('M')
    )

    parts = []
    run = []
    for ch in stripped:
        if ('a' <= ch <= 'z') or ('0' <= ch <= '9'):
            run.append(ch)
        elif run:
            parts.append(''.join(run))
            run.clear()
    if run:
        parts.append(''.join(run))

    joined = '-'.join(parts)[:max_length].rstrip('-')
    if not joined:
        return 'task'[:max_length]
    return joined
