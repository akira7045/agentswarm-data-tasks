# Implementation notes: retry-delays (#25)

Scope: `tasks/retry-delays/retry_delays.py` only (plus this note).

## Approach

- **Type checks first.** Every argument's type is validated before any value
  validation, so an invalid type always raises `TypeError` even when another
  argument is also out of range. `type(x) is int` rejects `bool` and int
  subclasses; `retry_after` must be `None` or `type(x) is str`.
- **Numeric header parsing, no `int()` on the whole string.** Leading/trailing
  ASCII space and horizontal tab are stripped, then every character must be an
  ASCII digit. The value is accumulated in 8-digit chunks with an early
  `> 1_000_000` bail-out, so arbitrarily long headers never trigger Python's
  int-to-str/str-to-int conversion limits and never surface overflow errors —
  they are simply rejected once the value exceeds the allowed range.
- **Bounds.** `0 <= attempts <= 32`, `0 <= base_ms <= cap_ms <= 1_000_000_000`,
  header seconds in `0..1_000_000` inclusive (`0`-`1000000` accepted with
  unlimited leading zeros).
- **Computation.** For `i` in `0..attempts-1`, `max(floor_ms, min(cap_ms,
  base_ms * 2**i))`. The exponential cap is applied *before* the server floor,
  so a large server delay may exceed `cap_ms`. Returns independent fresh
  lists; inputs are never mutated. `attempts == 0` still validates all types,
  ranges and the header, then returns `[]`.

Deliberately numeric-seconds only: no HTTP-date parsing, no current-time or
unit guessing, no jitter, sleep or network I/O.

## Verification

Pinned clean checker checkout at `ba63974691694e22cab62de26d6e3dcd07524f37`
(clean tree, scoped diff match), then:

```
PASS retry-delays: 84 exact cases and deterministic repeat probes
```

AI assistance disclosed in the PR.
