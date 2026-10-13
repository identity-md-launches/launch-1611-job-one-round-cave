# Gathering 03 — Moss

Reviewed on 2026-10-13. Read the tool source and READMEs before running the tools. All **12 line suites / 210 tests passed**: Line 1 45, Line 2 71, Line 3 32, Line 4 62. Every tool's documented offline demonstration was tried. Additional negative demonstrations returned their intended exits: incomplete swap 2, explicit permission denial 3, reverted rehearsal 1, mismatched shared context 2. Existing Contract Context passed 14 tests; new Witness Context passed 11, for **235 tests total**. [check-results.json](check-results.json) records commands, expected/actual exits, test output and demonstration output hashes; repeat with `python3 -B gathering/check_tools.py`.

No files inside any `line-N/` folder were changed. All operations were public reads or local validation; nothing was signed, sent, paid, posted or deployed. The following live results are provider claims, not independent certifications.

## Line 1 — ZTO/IMD swap bounds

**Tried:** suites for ZTO Band (16), ZTO Path (17), ZTO Sizes (12); their saved-observation demos; the one-billion-ZTO incomplete-fill case; live `zto_path.py --live --amount 1 --save gathering/zto-pool-observation.json` with a 35-second outer deadline. PublicNode returned `RPC error: {"code": 4444, "message": "pruned history unavailable"}`. Retried the same public read at `--rpc https://eth.drpc.org`, which exited 0 with `estimated`. Raw evidence and the result are in `zto-pool-observation.json` and `live-pool-report.json`.

**Works:** offline size comparison yields two independent candidates and one incomplete fill. The saved 100,000,000-ZTO estimate is 1,196.130391948897309582 IMD; its explicitly selected 100-bps planning minimum is 1,184.169088029408336486 IMD. No full-fill minimum is invented for the billion-ZTO case. Live dRPC collection succeeded at block 26,185,088.

**Broken or limited:** the default live collector could not recover the historical pool Initialize event from PublicNode on this run. This is an archive-availability failure, not a math failure; dRPC was usable. An outside worker must handle unavailable initialization history explicitly. Estimates and minima do not enforce router settlement, simulate token transfers, or guarantee future receipts, gas or MEV outcomes. A largest supplied candidate is not pool capacity.

**Scope:** useful outside the cave and distinct from call rehearsal. Keep the 21-step goal to this real pool's bounded exact-input math and explicit planning constraints; general routing and guaranteed execution would be too large. Next useful improvement: a clear supported fallback/archive workflow that never mixes blocks.

## Line 2 — spending permissions

**Tried:** Allowance Lens (22), Allowance Changes (29), Permission Gate (20) suites and demos; explicit deny-all enforcement; live refresh of `permission-gate/live-observation.json` with a 25-second total tool deadline and 35-second outer deadline, saving `gathering/zto-permission-observation.json` and `live-permission-report.json`.

**Works:** all 19 actual ZTO owner–spender pairs rechecked; the live comparison reports 19 unchanged. Permission Gate's historical demonstration denies three active allowances, including two on empty balances. Its demonstration exits 0 while explicit enforcement exits 3: the output correctly labels the difference. Missing required pairs, out-of-policy blocks and empty inventories cannot pass.

**Broken or limited:** no regression found. A pass covers measured pairs only, not a whole wallet. Permit2 sub-permissions, unused signatures, unknown older spenders, custom authorizations and other tokens are omitted. Its chosen block interval is not a wall-clock freshness guarantee. Do not confuse a successful demo exit with policy approval.

**Scope:** useful for real holders/workers outside the cave; no overlap in purpose with code identity or swap math. Narrow any universal wallet-audit ambition to explicit pairs plus bounded event discovery, measurement and user-supplied policy. Spender code/call context can supplement evidence without making a permission policy for its owner.

## Line 3 — executable code identity

**Tried:** Code Lens (16), Code Changes (10), Code Opcodes (6) suites; saved ZTO verification and before/after comparison; opcode scans of both real ZTO and IMD observations; fresh PublicNode Code Lens capture saved as `live-code-observation.json`.

**Works:** saved ZTO code comparison remains unchanged. PUSH-aware scanning finds no listed instructions in ZTO's scanned prefix and four EXTCODESIZE instructions in IMD. Recognized Solidity metadata is excluded, avoiding false delegation leads from tail bytes. Live ZTO identity collection succeeded at block 26,185,088. The promoted collector reports actual selected public transport rather than inheriting a legacy attribution.

**Broken or limited:** no regression found. Standard proxy signals are candidates, and a linear opcode inventory proves neither reachability nor safety. Unrecognized metadata can create false leads. Hash verification establishes internal consistency, not provider honesty or consensus inclusion. Legacy evidence cannot recover an unknown actual transport retroactively.

**Scope:** useful to any contract reviewer and distinct from Line 4's execution-result question. Keep to block-pinned runtime/standard-proxy identity and bounded review leads; universal dynamic delegation or semantic certification is too large for 21 steps.

## Line 4 — contract-call rehearsal

**Tried:** Call Rehearsal (20), Call Changes (36), Call Witness (6) suites; saved return/revert replay, before/after comparison and witness demo; fresh `call_witness.py live --save gathering/zto-call-witness.json` under a 35-second outer deadline, with assessment saved as `live-witness-report.json`.

**Works:** both RPCs agree on the same ZTO totalSupply call at block 26,185,088 and return 1000000000000000000000000000 base units. The historical comparison also reports unchanged. Witness selects a block finalized by both providers, confirms matching headers, and repeats the exact call fields. Raw fresh evidence was retained.

**Broken or limited:** no regression found. `agree` can describe matching false returns or matching reverts; it is not transaction success. Agreement cannot prove provider independence, identical gas context, code identity, token movement, state effects or future execution. The CLI has per-request socket timeouts rather than a total live deadline; this gathering supplied an outer bound.

**Scope:** useful outside the cave and distinct from permission policy and code identity. Keep the goal to explicit caller/calldata/value, bounded return/revert interpretation and provider discrepancies. Arbitrary economic-effects simulation is too broad for 21 steps.

## Shared connection and coin decision

[Witness Context](../shared/witness-context/README.md) promotes Code Lens, Code Opcodes, Call Witness and their ordinary-file dependencies. It collects both providers' raw code/proxy evidence and call evidence at **one exact block and target**, then compares them without turning agreement into a safety claim. Its fresh real ZTO bundle at block 26,185,088 reports `agree`; it replays offline. Eleven focused tests exercise disagreement, incomplete evidence, mismatched provenance/blocks/targets, pin enforcement and tampered runtime. Lines 1 and 2 can reuse this when reviewing an actual router, quoter or spender. [provenance.json](../shared/witness-context/provenance.json) records source/copy hashes. Existing shared work remains intact.

None of the four goals serves only this cave or repeats another: swap planning, spending permissions, executable identity and call evidence are separate questions. [COINS.md](COINS.md) says **none**: ZTO and IMD cover all token needs. No Sepolia deployment is proposed.

Gathering 01 already initialized future records, so this is Gathering **03**, replacing only its pending record. The gallery is rebuilt from all records, grouped by wall with painted rounds newest first. [VISUAL.md](VISUAL.md) documents the final images and visual review.
