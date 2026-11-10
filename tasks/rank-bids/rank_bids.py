"""Rank marketplace bids with explicit tie rules.

Orders bids by score descending, then bid ascending, then id in Python
Unicode lexicographic order ascending. Fully tied rows keep their input
order (stable sort). Strict exact-type validation runs before any bounds
check, and the input is never mutated.
"""


def rank_bids(bids):
    """Return the ids of ``bids`` ordered by score desc, bid asc, id asc."""
    if type(bids) is not list:
        raise TypeError("bids must be an exact list")
    keys = []
    for record in bids:
        if type(record) is not dict:
            raise TypeError("each bid must be an exact dict")
        record_keys = list(record.keys())
        if len(record_keys) != 3:
            raise TypeError("each bid must have exactly the keys id, bid, score")
        for key in record_keys:
            if type(key) is not str:
                raise TypeError("keys must be exact str")
        if set(record_keys) != {"id", "bid", "score"}:
            raise TypeError("each bid must have exactly the keys id, bid, score")
        ident = record["id"]
        bid = record["bid"]
        score = record["score"]
        if type(ident) is not str:
            raise TypeError("id must be an exact str")
        if type(bid) is not int:
            raise TypeError("bid must be an exact int")
        if type(score) is not int:
            raise TypeError("score must be an exact int")
        keys.append((-score, bid, ident))
    for record in bids:
        if record["bid"] < 0:
            raise ValueError("bid must be >= 0")
        if not 0 <= record["score"] <= 100:
            raise ValueError("score must be between 0 and 100")
    order = list(range(len(bids)))
    order.sort(key=lambda index: keys[index])
    return [bids[index]["id"] for index in order]
