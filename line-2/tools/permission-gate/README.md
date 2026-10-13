# Permission Gate

Check measured **ZTO spending permissions** against a worker's explicit allowance limits. A worker can use the result and exit code in a review or automated check. Python 3.10+ and its standard library are sufficient. This tool imports the adjacent Allowance Changes and Allowance Lens validators, both included in this repository. It performs no network access, wallet interaction or transaction preparation.

## One command to see it working

From the repository root:

```sh
python3 -B line-2/tools/permission-gate/permission_gate.py
```

This offline demonstration checks the bundled **real Ethereum ZTO inventory** against a deny-all policy. It prints `decision: deny`, **19 measured pairs and three violating permissions**, including two with empty balances. Demonstration mode exits **0** to show the tool working and labels its output `demonstration: true`. It is not an enforcement invocation. The full expected output is `example-report.json`.

## What happened when tried

The existing Allowance Changes refresh was run against its real saved inventory using the default **https://ethereum-rpc.publicnode.com**, a 25-second total deadline, its custom User-Agent and read-only hash-pinned calls. All 19 pairs across 16 owners were rechecked at Ethereum block **26,184,897**, timestamp **2026-10-13 16:54:47 UTC**, hash `0xbcad3af0fad3def330e01bef9d4352ae1fd1b1b1c17dad252205aecf2c807563`. The returned block numbers were decoded and validated by the capture tool. Allowances and balances matched the earlier block 26,184,324. Raw evidence is retained in `live-observation.json`, including calldata and returned words for each real owner and spender; no invented account is used.

Permission Gate denied three allowances under the empty allowlist. A test with explicit limits exactly equal to every measured allowance passed those 19 pairs. Lowering one positive limit by one base unit denied it. Removing required evidence returned `insufficient_evidence`, even with other known violations present. An actual saved empty Approval scan did not pass. **20 Permission Gate tests, 22 Allowance Lens tests and 29 Allowance Changes tests passed.** Test mutations are explicitly synthetic and are not saved as chain observations.

## Enforce a policy

```sh
python3 -B line-2/tools/permission-gate/permission_gate.py --observation line-2/tools/permission-gate/live-observation.json --policy line-2/tools/permission-gate/demo-policy.json
```

This specific invocation exits **3**, correctly denying the historical inventory under the bundled zero-allowance policy. For real use, supply your own policy and a newly captured raw observation; changing a historical policy's block interval does not make old evidence current. Both inputs must be within the current workspace and at most 96 KiB. This tool does not write files or silently fetch state.

| Exit | Meaning |
| --- | --- |
| 0 | Explicit enforcement passed the measured pairs; or the clearly labelled default demonstration completed |
| 1 | Invalid input, wrong identity, malformed raw evidence or file failure |
| 2 | Command-line usage error from argparse |
| 3 | Measured allowance violates a limit |
| 4 | Missing required pair, empty measurement or observed block outside the chosen interval |

All successful evaluations print a JSON report to stdout, including denied/insufficient decisions. Validation errors print JSON to stderr. If a shell is used for enforcement, check the exit code; piping stdout into a program can mask an exit code unless the shell's pipe handling preserves it.

## Policy format

`demo-policy.json` is a valid deny-all policy, pinned to the actual demonstration block. Its exact top-level fields are:

- `schema`: `permission-gate-policy-v1`.
- `chain_id`: integer `1`, Ethereum.
- `token_address`: real ZTO or IMD address; ZTO is the demonstration and first choice.
- `minimum_block`, `maximum_block`: inclusive nonnegative decimal **integer** block bounds selected by the worker.
- `pairs`: up to 64 entries, each with exactly `owner`, `spender`, and `maximum_allowance_raw`.

Owner and spender must be actual nonzero 20-byte addresses. `maximum_allowance_raw` is a **decimal string in token base units**, from `"0"` through the uint256 maximum. No exponent, float, sign or leading zero is accepted. One ZTO has 10^18 base units in this captured evidence. Use the validated observation's decimals when choosing your own limits. The tool never derives a permission ceiling from a balance or suggests an allowance to grant.

Every explicit policy pair must appear in the validated observation, including zero-ceiling pairs: an absent pair is unknown. An unlisted **measured** pair has a zero ceiling. Positive allowance on an empty balance still violates a zero ceiling because future receipts may be spendable. Equal allowance and ceiling passes. Duplicate policy pairs (including address case variants), duplicate JSON keys, extra/misspelled fields, wrong chain/token, noncanonical numbers and corrupt raw observations are rejected.

Observations can be a single raw Allowance Lens observation or a same-block Allowance Changes inventory. Derived report JSON is not evidence. The ancestor validators reject malformed calls, duplicate pairs, conflicting balances and mixed identity/block data before a policy is checked.

## Coverage and limits

`pass_measured_pairs` means precisely that the supplied measurements satisfy the supplied limits **at the reported block**. Every report has `complete_wallet_audit: false`. Unknown spenders outside the inventory, Permit2 sub-permissions, unused signatures, nonstandard authorizations, other tokens and chains remain outside coverage. This is a review of trusted RPC evidence, not a cryptographic proof or assurance that future spending is safe.

The explicit block interval prevents accidental acceptance of evidence outside a reviewed range. It does not check wall-clock age, block canonicality now or future state. Refresh through Allowance Changes before an actual current-state review, and deliberately choose the acceptable interval. This checker does not infer policy authority, prove spender trustworthiness, or change permissions.

Run checks:

```sh
python3 -B -m unittest discover -s line-2/tools/permission-gate -p 'test_*.py' -v
```
