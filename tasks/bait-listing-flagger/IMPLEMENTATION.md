# Implementation notes — bait-listing-flagger (#3)

Rule-based advisory classifier. No network, files, fixtures or packages; the
module only uses `re` and the stdlib.

## Approach

A listing is flagged only when some sentence contains an **affirmative
instruction** to perform a risky action. Signals are grouped by intent:

- Reveal/share key material (seed phrase, private key, recovery phrase).
- Post a payout/wallet address (or `<wallet-placeholder>`) in a claim/reply.
- Pay an unlock/deposit/verification/processing fee.
- Run/download/sync a payload from `<bare-host>`, or `curl ... | sh|bash`.
- Disable safety, security, sandbox or protections.

## Safety framing

- Titles explicitly prefixed `Warning:`, `Security guide:`, `Scam report:` or
  `Do not ` are treated as educational negatives.
- A sentence containing a negation/context cue (`never`, `do not`, `refuse`,
  `without`, `no downloads`, `must remain`, `should stay enabled`, `inert`,
  `synthetic`, `local`, `offline`, `risky`, `dangerous`) does not count as an
  affirmative instruction. This lets a safety sentence coexist with a later
  affirmative instruction in the body, which still flags the listing.
- A risky title alone flags only when the body has no inert/documentation cue
  (`test data`, `fixture`, `display`, `document`, `tutorial`, `explain`,
  `statistics`, `count`, `format`).

Matching is case-insensitive on a whitespace-collapsed, lowercased copy, so
case/whitespace changes and duplicated fields leave predictions unchanged.
No IDs, labels or fixture content are read.
