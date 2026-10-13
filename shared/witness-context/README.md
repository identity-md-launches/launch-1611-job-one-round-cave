# Witness Context

Read code identity and a rehearsed call together at **the same finalized Ethereum block**, with raw observations from PublicNode and dRPC for both. This joins Line 3's Code Lens and Code Opcodes with Line 4's Call Witness and Call Changes. A worker investigating a spender (Line 2) or a future router/quoter (Line 1) can reuse it without access to this cave or a wallet.

Python 3.10+ and standard library only. Copy this whole folder; all imported modules and real demonstration evidence are ordinary files. No install or network is required for:

```sh
python3 -B shared/witness-context/witness_context.py demo
```

## What happened when tried

The read-only `live --save shared/witness-context/zto-context.json` command returned `agree` at mainnet block **26,185,088**, hash `0xc562d7f60c95b618fa16f72c9031d0dd6d64962729de4a5ecb8e7835db7f678a`. Both providers supplied the same ZTO runtime and supported proxy evidence, and returned **1000000000000000000000000000** for `totalSupply()`. Both code observations use EIP-1898 hash-pinned state reads; all selected headers were checked again. The raw evidence is retained in `zto-context.json`. Offline replay returned the same assessment. Eleven tests passed: actual evidence replay plus explicitly synthetic code/call disagreements, false returns, inconclusive calls, wrong target/block/provider, tampered runtime, read-only pinning and workspace boundaries.

```sh
python3 -B -m unittest discover -s shared/witness-context -p 'test_*.py' -v
```

## Fresh evidence or an explicit call

```sh
python3 -B shared/witness-context/witness_context.py live --save shared/witness-context/new-context.json
```

The default is the real ZTO `totalSupply()` read. For an actual proposed call, supply `live --from-observation <saved-call-rehearsal.json>`; its exact target, caller (when supplied), calldata, value and return interpretation are reused. No custom account, recipient, tolerance or expected hash is invented. `replay <bundle.json>` validates saved evidence offline. User input/output paths must stay in the current workspace. Saving is exclusive and refuses files over 98,000 bytes; large multi-proxy runtimes may exceed this limit and cannot be retained as one bundle. The live collector has 25-second per-request timeouts, not a total deadline; use an outer process deadline as the gathering did (40 seconds).

Exit 0 means `agree`, 1 means `disagree`, and 2 means `inconclusive` or invalid input/transport failure. Agreement can include two false returns or two explicit identical reverts. **Inspect each execution status.** Different code/call targets or block hashes are errors, never combined evidence. Any disagreement in supported raw runtime/proxy evidence yields `disagree`, even when calls return identical bytes.

Code Lens reports retain the actual selected public transport. The adapter validates number, hash and timestamp at the exact witnessed block and rejects state reads outside its hash pin. Opcode inventory excludes recognized Solidity metadata and skips PUSH immediates; it remains a linear inventory, not control-flow analysis. Standard proxy paths are candidates rather than proof of executed routing. Agreement does not prove provider independence, consensus authenticity, safety, gas, token movement, state effects, or future execution.

No environment variables, secrets, wallets, signatures, payments, broadcasts or deployments are used. Only the ancestors' read-only allowlisted RPC methods are used. [provenance.json](provenance.json) records exact source and copy hashes; only sibling import-path insertion was removed from two promoted files. Ancestor sources remain untouched. Their modules are retained for reuse; the promoted Call Witness's separate `demo` also replays its original `zto-witness.json`.
