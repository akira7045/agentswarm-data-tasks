def ceil_div(number, divisor):
    if type(number) is not int or type(divisor) is not int:
        raise TypeError("number and divisor must be built-in int")
    if divisor <= 0:
        raise ValueError("divisor must be positive")
    return -((-number) // divisor)
