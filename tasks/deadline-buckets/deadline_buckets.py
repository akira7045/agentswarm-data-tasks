def deadline_buckets(deadlines, now):
    """Bucket integer-minute deadlines into urgency labels by offset from now.

    ``deadlines`` must be an exact built-in ``list`` of exact built-in ``int``
    values and ``now`` an exact built-in ``int``; subclasses, ``bool`` and any
    other type raise ``TypeError``. Negative and arbitrarily large timestamps
    are permitted. The result is a fresh list of ``str`` labels in input order,
    duplicates preserved: ``'expired'`` when ``deadline <= now``, ``'soon'``
    when ``now < deadline <= now + 60``, and ``'later'`` otherwise. Neither the
    input list nor ``now`` is mutated, and no state is shared between calls.

    >>> deadline_buckets([], 0)
    []
    >>> deadline_buckets([9, 10, 11, 70, 71], 10)
    ['expired', 'expired', 'soon', 'soon', 'later']
    >>> deadline_buckets([1, 1], 0)
    ['soon', 'soon']
    >>> deadline_buckets([-2, -1, 60], -1)
    ['expired', 'expired', 'later']
    """
    if type(deadlines) is not list:
        raise TypeError("deadlines must be an exact list")
    if type(now) is not int:
        raise TypeError("now must be an exact int")
    for deadline in deadlines:
        if type(deadline) is not int:
            raise TypeError("every deadline must be an exact int")
    boundary = now + 60
    result = []
    for deadline in deadlines:
        if deadline <= now:
            result.append("expired")
        elif deadline <= boundary:
            result.append("soon")
        else:
            result.append("later")
    return result
