def unique_tags(values):
    if type(values) is not list:
        raise TypeError("values must be an exact built-in list")
    for item in values:
        if type(item) is not str:
            raise TypeError("every element must be an exact built-in str")
    seen = set()
    result = []
    for item in values:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
