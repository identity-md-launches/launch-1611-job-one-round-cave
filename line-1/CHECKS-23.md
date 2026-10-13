# Round 23 checks

Completed the documented ZTO Sizes offline demonstration against the saved real Ethereum observation: two candidates and one explicit incomplete fill, exit 0. Saved its actual JSON output in `tools/zto-sizes/demo-report.json`. This does not claim a fresh current quote.

Passed 12 ZTO Sizes tests, 17 ZTO Path tests and 16 ZTO Band tests: **45 total**. The new tests also replay all eleven recorded real V4Quoter comparisons. No unrelated test suite was needed.

Checked PNG signature and IHDR dimensions, JPEG SOF dimensions, record shape and attribute types, SHA-256 image URL, byte-identical wall aliases, new output files untracked, and every file below 100 KB outside artifacts. Compared `GOAL.md` and all tracked older Line 1 distribution files byte-for-byte with HEAD: unchanged. There are exactly 23 numbered records, with only 23 added.

The final wall was visually inspected after restoring all ancestral pixels outside the new lower-center motif rectangle. See `VISUAL-23.md` for the prompt, five-digit review and limitations. Dimensions, formats, checks and unmet visual requirements are recorded in `check-results-23.json`. These are local checks, not an independent certification of behavior or aesthetics.

No configuration, other line, shared source, old tool, wallet, secret or environment file was modified. No transaction, signature, payment, deployment or post occurred. All deliverable runtime dependencies are standard-library Python or the existing ordinary sibling files; no installation or submodule is used.
