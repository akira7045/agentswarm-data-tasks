import json
import re

_ID_RE = re.compile(r"[a-z][a-z0-9-]{0,31}")


class _DuplicateKey(ValueError):
    pass


def _pairs_hook(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise _DuplicateKey(key)
        obj[key] = value
    return obj


def _reject_constant(name):
    raise ValueError("non-finite number: " + name)


def _decode(text):
    decoder = json.JSONDecoder(object_pairs_hook=_pairs_hook, parse_constant=_reject_constant)
    start = len(text) - len(text.lstrip(" \t\n\r"))
    try:
        value, end = decoder.raw_decode(text, start)
    except _DuplicateKey:
        raise ValueError("duplicate object key") from None
    except ValueError:
        raise ValueError("invalid JSON") from None
    except RecursionError:
        raise ValueError("invalid JSON") from None
    if text[end:].strip(" \t\n\r"):
        raise ValueError("trailing data")
    return value


def _validate(value):
    if type(value) is not dict:
        raise ValueError("root must be an object")
    if set(value) != {"id", "title", "budget"}:
        raise ValueError("expected exactly id, title, budget")
    ident = value["id"]
    if type(ident) is not str or _ID_RE.fullmatch(ident) is None:
        raise ValueError("invalid id")
    title = value["title"]
    if type(title) is not str:
        raise ValueError("invalid title")
    if not 1 <= len(title) <= 80 or not title.strip():
        raise ValueError("invalid title")
    budget = value["budget"]
    if type(budget) is not int or budget < 0:
        raise ValueError("invalid budget")
    return {"id": ident, "title": title, "budget": budget}


def parse_task(text):
    if type(text) is not str:
        raise TypeError("text must be a built-in str")
    return _validate(_decode(text))
