# deadline-parser implementation notes

Implements `parse_deadline(text, now)` per `SPEC.md` using only the standard
library. No wall clock, network, locale data or fixture access.

## Approach

- Normalise with `text.strip().lower()`; compare whole strings only, so internal
  spacing (`"Nov  13"`) and any trailing prose are rejected.
- `now` is converted to UTC with `astimezone` before all calendar arithmetic.
- Each supported form is matched with a full-match regex:

  - `Nov 13 12:00 UTC`
    - Parsed manually (not `strptime`, which accepts extra forms).
    - Month must be a known three-letter English name; day is 1–2 digits.
    - An invalid date in the current year returns `None` (no leap-year search).
    - If the candidate is strictly before `now`, the same month/day is taken in
      `now.year + 1` (again returning `None` if that date is invalid).
  - `2026-11-13T12:00[:SS][Z|±HH:MM]`
    - Seconds optional; `Z` or a numeric offset is required.
    - Offset hours 00–23 and minutes 00–59 are range-checked before building the
      offset; the value is normalised to UTC.
    - Rejects naive dates, fractional seconds and trailing text.
  - `in N days`
    - `N` is a nonnegative decimal integer, max 3650 (leading zeros allowed).
    - Uses `timedelta(days=N)`, preserving the UTC hour/minute/second.
  - `end of week`
    - Sunday 23:59:59 of the current UTC Monday–Sunday week. On Sunday this is
      the same day.
  - `none` (any case) and every other value return `None`.

## Output

UTC strings formatted exactly `YYYY-MM-DDTHH:MM:SSZ` (seconds always present).

## Verification

```
$ python3 tasks/deadline-parser/check.py --solution "$PWD/tasks/deadline-parser/deadline_parser.py"
PASS deadline-parser: 64 exact cases at fixed now + 8 fixed calendar probes
```

The pinned trusted checker at `e5fcaa8d0dbcf7845506aebe486fc341f50d4316`
(cloned separately, clean tree) produces the same PASS output.

AI assistance was used to write this implementation; it was reviewed and tested
against the pinned checker above.
