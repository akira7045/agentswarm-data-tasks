# JSON Pointer implementation notes

RFC 6901 string-pointer lookup over an in-memory JSON tree.

## Approach
- Validate pointer type first: exact built-in `str` only; any subclass raises `TypeError`.
- Empty pointer returns the document unchanged (same object identity).
- Non-empty pointer must start with ASCII `/`, else `ValueError`.
- Split the remainder on literal `/`, preserving empty tokens, then decode **all** tokens
  (`~1` -> `/`, `~0` -> `~`, any other `~` sequence including a trailing `~` ->
  `ValueError`) before any traversal, so syntax errors win over missing paths.
- Decode is single-pass: `~01` -> literal `~1` (not slash).
- Traverse one token at a time:
  - dict: exact case-sensitive key membership; missing -> `KeyError`.
  - list: token must be `0` or `[1-9][0-9]*`; leading zeros, signs, whitespace, Unicode
    digits, empty tokens and `-` are rejected (`KeyError`). Oversized digit strings are
    length-checked against `len(str(length))` before `int()`, so no `OverflowError` or
    conversion-limit error leaks; out-of-bounds indices -> `KeyError`.
  - scalar: descending raises `KeyError`.
- No mutation, copying, coercion or normalization; containers may alias the document.

## Verification
Trusted clean checkout pinned to `ba63974691694e22cab62de26d6e3dcd07524f37`
(HEAD/clean/scoped-diff all confirmed), run offline:

```
PASS json-pointer: 90 exact cases and deterministic repeat probes
```

Extra probes beyond fixtures: empty list index, `00`/`03` leading zero, `len` boundary,
scalar descent, `~`/`~2` invalid escapes, `#/a` fragment rejection, 5000-digit token,
Unicode keys, root/container identity, and non-mutation.

AI-assisted contribution (disclosed).
