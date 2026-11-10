# rank_bids — implementation notes

Approach:
- Validate the container first: `bids` must be an exact `list` (`type is list`), otherwise `TypeError`.
  List subclasses are rejected even when empty.
- Shape/type pass (before bounds): each record must be an exact `dict`; every key must be an exact
  `str`; the key set must be exactly `{id, bid, score}` (a `len`+per-key `type is str` check defeats
  `str`-subclass keys that compare equal in a set). `id`/`bid`/`score` must be exact `str`/`int`/`int`,
  which excludes `bool` and all subclasses. Any violation raises `TypeError`.
- Bounds pass (after all shapes/types pass): `bid >= 0` and `0 <= score <= 100`, else `ValueError`.
  Running bounds strictly after the type pass guarantees a shape/type error wins over a bounds error
  in a mixed batch.
- Ordering: build `(-score, bid, id)` keys, sort an index list (Python's stable, Unicode-lexicographic
  for `id`), then emit ids. Full ties preserve input order and duplicates; integer math is
  arbitrary precision; the input is never mutated and each call returns a fresh list.

Verified with the pinned clean checker at `89e645f8bba9a51b4880bcf541f20db16540c373`:

```
PASS rank-bids: 31 fixtures plus exact type, subclass, independence and doctest probes
```

AI assistance was used to author this change.
