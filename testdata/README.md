# Test photos

> **DUMMY WALLET — NEVER FUND IT.**
> Every photo here shows the same dummy plate (BIFB TREASURY X, fingerprint C212E86B), engraved
> in 2024 for testing and never funded. Its 12 words are public in this repository, so anything
> sent to it can be taken by anyone.

`expected.json` lists the plate's words and what each photo should give (`read` or `fail`).
`../prototype/run_tests.py` checks every photo against it.

## Adding photos

- **Dummy plates only.** Never photograph a plate that holds, or will hold, funds.
- Name them `dummy-NN-short-description.jpg` and add an entry to `expected.json`.
- A photo of a different dummy plate needs its own `words` entry: split `expected.json`
  per plate when that happens.
- Pi camera photos from `../plate-capture` are the most useful: that's the camera the reader
  will run on.
