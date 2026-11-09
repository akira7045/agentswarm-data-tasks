# Implementation notes: normalize_headers

Referenced in PR for issue #27. Python 3.11+ standard library only.

## Approach

`normalize_headers(headers)`:

1. **Type validation.** `type(headers) is not list` -> `TypeError`; then every
   element is checked with `type(item) is not str` -> `TypeError`. Exact-type
   checks reject list/str subclasses, tuples, `bool`, `None`, numbers and
   containers. All items are validated before any output is produced, so an
   error never leaves partial state.
2. **Per-header normalization** (`_normalize_one`):
   - `unicodedata.normalize("NFKC", header)` then `.casefold()` (in that order,
     as specified). NFKC folds full-width forms and precomposed/decomposed
     accents; casefold expands e.g. `ß` -> `ss`.
   - A single scan replaces each *maximal run* of characters outside ASCII
     `a`-`z` and `0`-`9` with one `_`. Existing underscores are part of such a
     run, so `A__-- B` -> `a_b`.
   - `.strip("_")` removes leading/trailing replacement underscores; an empty
     result becomes `column`.
   - Lone surrogates and NUL simply fall in a non-ASCII run and are collapsed,
     which is why e.g. `a\ud800b` -> `a_b`.
3. **Uniqueness (emit-only).** `used` starts empty. For each base name, if it is
   already used, try `base + "_2"`, `base + "_3"`, ... until the first unused
   name. Only already-emitted names are tracked, so `['A','A','A_2','A']` ->
   `['a','a_2','a_2_2','a_3']`. The whole base (including any numeric suffix) is
   kept unchanged when suffixing.

The return value is a fresh `list` of fresh `str` objects; the input is never
mutated, and repeated calls return equal but independent lists.

## Verification

Pinned-check command from the issue, using a separate clean checkout at
`a4cc69241d9abb14ed5aad0c1e2470a4c4989404`:

```
PASS csv-headers: 73 exact cases and deterministic repeat probes
```

The check also exercises the subclass/tuple rejection probes in `worker.py`.
