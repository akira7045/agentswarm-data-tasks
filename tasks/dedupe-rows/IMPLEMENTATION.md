# Implementation notes — dedupeRows

`export function dedupeRows(rows, keyIndex)` in `dedupe_rows.mjs`.

## Approach
1. **Shape validation first (before bounds).** Each candidate array must be a
   dense normal `Array`:
   - reject Proxies via `util.types.isProxy` (this catches plain and revoked
     proxies, since they otherwise forward `Array.isArray`, prototype and
     indexed access transparently);
   - `Array.isArray` true;
   - `Object.getPrototypeOf` exactly `Array.prototype` (rejects subclasses,
     null/altered prototypes);
   - `Object.keys(value).length === value.length` and a `hasOwnProperty` index
     check on every slot (rejects holes / sparse arrays and extra named props).
   Applied to `rows` and to every row. Non-conforming values raise `TypeError`.
2. **Type validation.** `keyIndex` must be a primitive `number` (boxed
   `Number`, subclasses, bigint, symbol, string, etc. raise `TypeError`). Every
   row cell must be a primitive `string` (`typeof === 'string'`, so boxed
   strings and subclass instances raise `TypeError`).
3. **Bounds.** `keyIndex` must be a nonnegative safe integer and every row must
   have an element at that index; otherwise `RangeError`. Empty `rows` accepts
   any valid nonnegative safe `keyIndex`.
4. **Dedupe.** Walk rows in order, track seen key strings in a `Set` using exact
   JS string equality (no trimming/case-folding/normalization), keep the first
   occurrence, and emit fresh normal dense row copies. Inputs are never mutated
   and never retained; frozen inputs work because we only read.

## Verification
Public and pinned trusted checkers both pass:

```
PASS dedupe-rows: 8 fixtures plus exact types, proxies, subclasses, holes and boundary probes
```

Run with Node 22 against a clean trusted checkout pinned to
`f4dfe02fb13d8214bf46fd44b2d2208028ca6ff9`.
