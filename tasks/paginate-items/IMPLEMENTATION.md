# paginate-items implementation

## Approach

`paginate_items(items, offset, limit)` fixes the seeded implementation in three ways:

1. **Exact builtin typing.** Rejects non-`list` `items`, non-`int` `offset`/`limit`, non-`str` elements, and any subclass (including `bool`, which is an `int` subclass) via `type(x) is T`. All type checks run before any range checks so wrong types always raise `TypeError`, never `ValueError`.
2. **Correct `next_offset`.** The bug was `offset+limit <= len(items)`, which returned a bogus next offset on an exactly-full final page. A next offset is returned only when more items remain: `end < len(items)`, i.e. strictly fewer. Empty input, offset at/past the end, and an exactly full final page all yield `None`.
3. **Bounds/grammar -> ValueError.** After typing passes, enforce `len(items) <= 1000`, each `str` at most 64 code points, `offset` in `[0, 1000000000]`, `limit` in `[1, 1000]`.

## Properties

- Returns a fresh `dict` with exactly the keys `items` and `next_offset`; `items` is a fresh `list` slice (no aliasing to the input).
- Preserves order and duplicates.
- No input mutation, no retained state, no I/O, stdlib only.

## Verification

- In-tree: `python3 tasks/paginate-items/check.py --solution ...` -> `PASS` (8 examples + exact type, bounds, isolation probes).
- Trusted checkout pinned to `ed676e23b94c290e3f96df25133045feae892f80` (clean, diff-clean vs pin): same `PASS`.
