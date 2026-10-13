# ZTO Sizes

Compare up to 20 independent ZTO/IMD swap sizes at one observed Ethereum block. For each full fill, calculate a minimum-output planning number using your explicit slippage tolerance, and optionally reject sizes whose fee-inclusive loss from the initial pool spot ratio exceeds your chosen limit. Incomplete fills and zero output bounds never become usable candidates.

## One command to see it working

From the repository root, using Python 3.10+:

```sh
python3 -B line-1/tools/zto-sizes/zto_sizes.py --amount 1 --amount 100000000 --amount 1000000000 --slippage-bps 100
```

This uses the bundled **real historical ZTO Path observation at Ethereum block 26,184,260**. No network or installation is needed. The one-hundred-million ZTO case estimates **1,196.130391948897309582 IMD**, with a planning minimum of **1,184.169088029408336486 IMD** at the demonstration's explicitly supplied 100-basis-point tolerance. The one-billion ZTO case is incomplete and supplies no minimum. These are examples, not recommended sizes or a suggested tolerance.

Use `--input IMD` for the reverse direction, `--max-spot-loss-bps 200` for an optional exact loss filter, and `--snapshot <workspace-path>` for another ZTO Path observation. The default path is resolved relative to the tool, while user-selected paths must remain inside the current workspace. Keep the sibling `zto-path/` and `zto-band/` folders when copying this tool. All dependencies are ordinary repository files and all runtime imports use only the Python standard library.

## What the numbers mean

Each candidate starts with identical liquidity, square-root price and tick coverage. Candidates do not simulate successive trades. ZTO is the default input; IMD is the other real pool currency. Pool identity, on-chain decimals, static fees, hook permissions and tick coverage are validated by the ancestor tools.

Minimum output is `floor(estimated_output_raw * (10000 - slippage_bps) / 10000)`. Tolerance must be explicitly supplied as an integer from 0 through 9999. Floor rounding can make the permitted raw-unit loss slightly larger than the nominal percentage; a zero minimum is refused. This is a number a worker can later review for a router constraint; this tool neither builds nor enforces that constraint.

The gross spot baseline is input times the initial raw output/input pool price ratio. The fee-inclusive spot loss compares estimated output with that baseline, incorporating pool fees, curve movement and integer rounding. It is **separate from slippage tolerance**, excludes external prices, and is reported as an exact rational with a ceiling in basis points. Filtering compares the rational, not a floating-point approximation. Raw amounts and rational components are decimal strings. Both token directions use actual recorded decimals for presentation.

`largest_candidate_input_raw` means the largest **supplied** amount passing the filters. It is not a capacity search or a trade recommendation. Repeated amounts remain repeated and ordering is preserved. Errors reject the entire request; invalid amounts are not silently skipped. Exit 0 means at least one candidate; exit 2 means no usable candidate; exit 1 means invalid input or snapshot. CLI syntax errors also exit 2 via argparse. JSON reports go to stdout; validation errors go to stderr.

## What happened when tried

The documented demonstration returned two candidates and one explicit `outside_coverage` partial fill. All **12 new tests passed**. They replay all 11 saved same-block real V4Quoter outputs, check exact raw-unit floor inequalities, both token directions, zero outputs, exact rational loss filtering, unordered and repeated amounts, independent simulations, invalid inputs, corrupt pool identity, offline operation and exit codes. The ancestor suites still passed **16 + 17 tests**, for **45 tests total**.

```sh
python3 -B -m unittest discover -s line-1/tools/zto-sizes -p 'test_*.py' -v
```

`demo-report.json` retains the actual documented output. No fresh live observation is claimed. To collect fresh data, use ZTO Path's documented read-only collector, then pass its snapshot here. This tool has no network, environment, key, wallet, signing, sending or file-writing code.

The snapshot is historical RPC evidence, not a current quote, cryptographic proof or receipt guarantee. Core pool estimates do not account for router settlement, token transfer behavior, gas, MEV or later liquidity changes. For pool addresses, raw evidence, original math sources and MIT notices, see the sibling [ZTO Path README](../zto-path/README.md) and [ZTO Band README](../zto-band/README.md).
