"""Plan capped exponential retry delays with a numeric Retry-After floor.

Offline, deterministic, standard library only. Never sleeps or performs I/O.
"""

_MAX_ATTEMPTS = 32
_MAX_MS = 1_000_000_000
_MAX_FLOOR_SECONDS = 1_000_000
_STRIP = " \t"


def _require_int(name, value):
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact int")


def _parse_floor(retry_after):
    if retry_after is None:
        return 0
    if type(retry_after) is not str:
        raise TypeError("retry_after must be None or an exact str")

    text = retry_after.strip(_STRIP)
    if not text:
        raise ValueError("retry_after must contain ASCII digits")
    for ch in text:
        if ch < "0" or ch > "9":
            raise ValueError("retry_after must contain only ASCII digits")

    chunk = 8
    value = 0
    for start in range(0, len(text), chunk):
        piece = text[start : start + chunk]
        value = value * (10 ** len(piece)) + int(piece)
        if value > _MAX_FLOOR_SECONDS:
            raise ValueError("retry_after exceeds the allowed range")
    return value


def retry_delays(attempts, base_ms, cap_ms, retry_after):
    _require_int("attempts", attempts)
    _require_int("base_ms", base_ms)
    _require_int("cap_ms", cap_ms)
    floor_ms = _parse_floor(retry_after) * 1000

    if not 0 <= attempts <= _MAX_ATTEMPTS:
        raise ValueError("attempts out of range")
    if not 0 <= base_ms <= cap_ms <= _MAX_MS:
        raise ValueError("require 0 <= base_ms <= cap_ms <= 1000000000")

    return [max(floor_ms, min(cap_ms, base_ms * 2**i)) for i in range(attempts)]
