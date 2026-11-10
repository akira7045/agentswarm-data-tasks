# Implementation notes: slug normalizer

`normalize_slug(text, max_length=64)` in `slug_normalizer.py`.

## Approximate approach

1. Validate arguments first: `type(text) is str` and `type(max_length) is int`
   (exact types, so `bool` is rejected), then `1 <= max_length <= 128`.
   Wrong types raise `TypeError`, out-of-range raises `ValueError`.
2. `text.casefold()`, then `unicodedata.normalize('NFKD', ...)`, then drop every
   codepoint whose `unicodedata.category` starts with `M` (combining marks are
   removed, not treated as separators).
3. Walk the result and collect maximal runs of ASCII `[a-z0-9]`. Every run of
   any other character is collapsed by simply joining adjacent runs with a single
   hyphen, which both trims edge separators and merges separator runs.
4. Truncate the joined slug to `max_length`, then `rstrip('-')` so truncation
   never leaves a trailing hyphen.
5. If the result is empty, return `'task'[:max_length]`.

## Notes

- The input is never mutated; all work is on new strings.
- The function is pure and deterministic, so repeated calls return equal values.
- Casefold before NFKD matters for cases like `İstanbul` (`i` + combining dot ->
  `istanbul`) and `ß` -> `ss`.
- Verified with the in-tree checker and with a clean trusted checker checkout
  pinned to `e3f7c95e3330e6a7c753c00cfad6cfc606dc75de`: 76 exact cases PASS.
  Extra manual probes covered idempotence, non-mutation, exact-type rejection,
  and length-boundary truncation.
