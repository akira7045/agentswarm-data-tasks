def group_indices(values):
    if type(values) is not list:
        raise TypeError("values must be a list")
    for value in values:
        if type(value) is not str:
            raise TypeError("every element must be a str")
    result = {}
    for index in range(len(values)):
        value = values[index]
        if value in result:
            result[value].append(index)
        else:
            result[value] = [index]
    return result
