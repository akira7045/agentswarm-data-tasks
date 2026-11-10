def _require_dict(obj):
    if type(obj) is not dict:
        raise TypeError("expected exact dict")


def _require_size(obj):
    if len(obj) > 1000:
        raise ValueError("dict has more than 1000 entries")


def _require_type(key, value):
    if type(key) is not str:
        raise TypeError("expected exact str key")
    if type(value) is not int:
        raise TypeError("expected exact int value")


def _require_bounds(key, value):
    if len(key) > 64:
        raise ValueError("key longer than 64 code points")
    if value < 0 or value > 1000000000:
        raise ValueError("count out of range [0, 1000000000]")


def merge_counters(left, right):
    _require_dict(left)
    _require_dict(right)
    for k, v in left.items():
        _require_type(k, v)
    for k, v in right.items():
        _require_type(k, v)
    _require_size(left)
    _require_size(right)
    for k, v in left.items():
        _require_bounds(k, v)
    for k, v in right.items():
        _require_bounds(k, v)
    result = {}
    for k, v in left.items():
        result[k] = v
    for k, v in right.items():
        if k in result:
            result[k] = result[k] + v
        else:
            result[k] = v
    return result
