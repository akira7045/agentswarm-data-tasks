def chunk_ranges(length, size):
    if type(length) is not int or type(size) is not int:
        raise TypeError('exact integers required')
    if length < 0 or size < 1:
        raise ValueError('invalid bounds')
    return [
        (start, min(start + size, length))
        for start in range(0, length, size)
    ]
