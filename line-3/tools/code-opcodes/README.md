# Code Opcodes

Inspect the executable bytes in a verified Code Lens observation for instructions that may change where code runs. The scan skips `PUSH1`–`PUSH32` immediate bytes and recognizes a fully parsed Solidity CBOR metadata tail before looking for `DELEGATECALL`, `CALLCODE`, external-code inspection, creation, and destruction instructions. A `DELEGATECALL` or `CALLCODE` in a node with no supported proxy signal becomes an `unresolved_delegation_signal` for manual review. It does **not** claim the instruction can be reached.

One command from the repository root shows it working offline on a saved, real ZTO observation:

```sh
python3 -B line-3/tools/code-opcodes/code_opcodes.py --report line-3/tools/code-lens/zto-observation.json
```

Python 3.9+ and the standard library are sufficient. Keep the sibling `code-lens/` folder: its verifier and Keccak implementation are ordinary committed dependencies. The report must resolve inside the current workspace. This tool makes no network request and never signs, sends, pays, posts, or reads a wallet, secret or environment variable.

## What happened when tried

The saved ZTO observation at finalized Ethereum block 26,183,813 verified. Its 1,287-byte runtime has a recognized 12-byte Solidity 0.8.26 metadata tail and no listed instruction in the scanned prefix. The same command with `imd-observation.json` verified IMD's 22,990-byte runtime and found four `EXTCODESIZE` instructions (offsets 6113, 6483, 8161, 13280), with no delegation instruction in its scanned prefix. The IMD metadata tail contains bytes that look like `CREATE` and `CALLCODE` if scanned naively; this tool correctly excludes that fully parsed 53-byte tail. Six local tests passed, including a real-report check, PUSH immediate exclusion, a synthetic true `DELEGATECALL`, and tampered-report rejection.

Run the checks:

```sh
python3 -B -m unittest discover -s line-3/tools/code-opcodes -p 'test_*.py' -v
```

An opcode's presence is a review lead, not proof of reachable delegation. Its absence in this linear scan does not establish semantic safety, identify code reached through other contracts, prove consensus authenticity, or rule out custom routing. Unrecognized metadata is scanned as bytes, so a future or unusual compiler tail can create false leads. Code Lens report verification establishes internal consistency only; it trusts the original RPC observation. Reobserve code before acting on an old report.

The mark's meaning: Pepe finds a hidden fork before trusting the stone path.
