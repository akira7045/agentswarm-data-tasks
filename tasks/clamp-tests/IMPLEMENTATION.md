# clamp-tests implementation notes

Scope: only `tasks/clamp-tests/tests_submission.py` (plus this note). No changes
to the implementation, spec, checker or fixtures.

Approach: assert only the documented public behavior, grouped into three
`unittest.TestCase` classes so every mutant is killed by a spec-faithful
assertion rather than by targeting a mutant identity.

- Return value / clipping: value inside the range is returned unchanged; below
  lower clips to lower; above upper clips to upper; equal bounds are valid and
  clamp to that bound; negative in-range values are not absolute-valued; the
  result is an exact built-in `int`.
- Bounds: reversed bounds raise `ValueError`, including when the value sits
  outside the interval; equal bounds are accepted.
- Types: bool, float, str, None and containers raise `TypeError` in every
  argument position; types are validated before the reversed-bounds comparison
  (`clamp(None, 5, 2)` and `clamp(True, 5, 2)` raise `TypeError`).

Verification (offline, pinned checker `1a8b2feba3c639059d30dfe9d5fd9d7c8451d9be`):

```
PASS clamp-tests: reference passed; 10/10 implementation mutants killed
```

No third-party packages, subprocesses, networking, fixtures, or implementation
source inspection are used.
