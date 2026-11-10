# deadline_buckets — implementation notes

`deadline_buckets(deadlines, now)` maps integer-minute timestamps to urgency
labels relative to `now`, returning a fresh list in input order with duplicates
preserved.

## Approach

- **Strict input contracts first.** `type(deadlines) is not list` →
  `TypeError`; `type(now) is not int` → `TypeError`; then every element must
  satisfy `type(deadline) is int`. Using the identity check (`type(x) is T`)
  rather than `isinstance` rejects `bool` (a subclass of `int`) and any
  `list`/`int` subclasses exactly as the spec requires, while still allowing
  negative and arbitrary-precision integers.
- **Boundaries.** With `boundary = now + 60`: `deadline <= now` → `'expired'`,
  else `deadline <= boundary` → `'soon'`, else `'later'`. These are integer
  comparisons only; the clock is never consulted and no dates are parsed.
- **No shared state / no mutation.** The result is a newly built list; inputs
  are read-only, so a caller mutating the returned list cannot affect
  subsequent calls. Empty input yields an empty list.

## Verification

Run against the trusted pinned checker at
`89e645f8bba9a51b4880bcf541f20db16540c373`:

```
PASS deadline-buckets: 14 fixtures plus exact type, subclass, independence and doctest probes
```

The function carries runnable docstring examples covering the spec cases
(empty list, mixed buckets, duplicates, negatives).

## AI assistance

This contribution was produced with AI assistance (implementation draft,
edge-case review, and verification run), disclosed per CONTRIBUTING.md.
