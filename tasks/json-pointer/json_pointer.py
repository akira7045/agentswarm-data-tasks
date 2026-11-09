"""RFC 6901 JSON Pointer lookup over an in-memory JSON tree."""


def _decode_token(raw):
    if '~' not in raw:
        return raw
    out = []
    i = 0
    n = len(raw)
    while i < n:
        ch = raw[i]
        if ch == '~':
            if i + 1 >= n:
                raise ValueError('dangling ~ in token')
            nxt = raw[i + 1]
            if nxt == '0':
                out.append('~')
            elif nxt == '1':
                out.append('/')
            else:
                raise ValueError('invalid ~ escape in token')
            i += 2
        else:
            out.append(ch)
            i += 1
    return ''.join(out)


def _parse_index(token, length):
    if token == '':
        raise KeyError('empty array token')
    first = token[0]
    if first != '0' and (first < '1' or first > '9'):
        raise KeyError(token)
    for ch in token:
        if ch < '0' or ch > '9':
            raise KeyError(token)
    if token == '0':
        value = 0
    else:
        if first == '0':
            raise KeyError(token)
        digits = token.lstrip('0')
        if len(digits) > len(str(length)):
            raise KeyError(token)
        value = int(digits)
    if value >= length:
        raise KeyError(token)
    return value


def json_pointer_get(document, pointer):
    if type(pointer) is not str:
        raise TypeError('pointer must be str')
    if pointer == '':
        return document
    if pointer[0] != '/':
        raise ValueError('pointer must be empty or start with /')
    raw_tokens = pointer[1:].split('/')
    tokens = [_decode_token(tok) for tok in raw_tokens]

    current = document
    for token in tokens:
        if type(current) is dict:
            if token not in current:
                raise KeyError(token)
            current = current[token]
        elif type(current) is list:
            current = current[_parse_index(token, len(current))]
        else:
            raise KeyError(token)
    return current
