def paginate_items(items, offset, limit):
    if type(items) is not list:
        raise TypeError("items must be a list")
    if type(offset) is not int:
        raise TypeError("offset must be an int")
    if type(limit) is not int:
        raise TypeError("limit must be an int")

    for value in items:
        if type(value) is not str:
            raise TypeError("items must contain str")
    if len(items) > 1000:
        raise ValueError("too many items")
    for value in items:
        if len(value) > 64:
            raise ValueError("item too long")
    if offset < 0 or offset > 1000000000:
        raise ValueError("offset out of range")
    if limit < 1 or limit > 1000:
        raise ValueError("limit out of range")

    end = offset + limit
    page = items[offset:end]
    next_offset = end if end < len(items) else None
    return {"items": page, "next_offset": next_offset}
