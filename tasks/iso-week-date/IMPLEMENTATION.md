# Implementation notes: ISO week date -> calendar date

## Approach
- Validate **all** argument types first (`type(x) is int`), so a wrongly typed
  argument raises `TypeError` even when another argument is numerically out of
  range (type precedence per SPEC).
- Range-validate year (1..9999), week (1..53), day (1..7).
- Week 53 is accepted only for ISO years that actually have 53 weeks: the
  year starts on Thursday, or is a leap year starting on Wednesday (checked via
  Jan 1 weekday).
- Anchor on Jan 4 (always in ISO week 1), back up to that week's Monday, then
  advance `(week-1)*7 + (day-1)` days using integer ordinals.
- Convert ordinals via `datetime.date.fromordinal`, catching overflow so that
  `(9999, 52, 6)` / `(9999, 52, 7)` (calendar year 10000) raise `ValueError`
  rather than `OverflowError`.

## Result
`PASS iso-week-date: 198 exact cases and deterministic repeat probes`

Additionally cross-checked ~45k valid ISO week dates (years 1-59, 1990-2049,
9900/9998/9999) against Python's own `date.isocalendar()` round-trip: no
mismatches. The only two "errors" were `(9999,52,6)` and `(9999,52,7)`, which
the SPEC explicitly declares invalid.
