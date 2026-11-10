def platform_fee(amount):
    """Return the marketplace platform fee in integer cents.

    The fee is ``ceil(amount * 3 / 100)`` computed with exact integer
    arithmetic only, so no floating point rounding is involved and
    arbitrarily large amounts stay exact.

    ``amount`` must be an exact built-in ``int`` in integer cents and
    greater than or equal to zero. Booleans, ``int`` subclasses and every
    other type raise ``TypeError``; negative integers raise ``ValueError``.

    >>> platform_fee(0)
    0
    >>> platform_fee(100)
    3
    >>> platform_fee(101)
    4
    """
    if type(amount) is not int:
        raise TypeError("amount must be an exact int")
    if amount < 0:
        raise ValueError("amount must be non-negative")
    return (amount * 3 + 99) // 100
