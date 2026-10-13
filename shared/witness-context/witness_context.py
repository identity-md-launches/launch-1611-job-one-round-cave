#!/usr/bin/env python3
"""Join two-provider code identity and call evidence at exactly one block."""
import argparse
import json
from pathlib import Path
import sys
import call_witness as witness
import code_lens as code
import code_opcodes as opcodes

core = witness.core
SCHEMA = 'witness-context-v1'
LIMIT = 98_000
HERE = Path(__file__).resolve().parent


class PinnedCode:
    """Adapt Code Lens's finalized selector to the witnessed finalized block."""
    def __init__(self, rpc, selected):
        self.rpc, self.endpoint = rpc, rpc.endpoint
        self.selected = core.header(selected)
        self.pin = {'blockHash': self.selected['hash'], 'requireCanonical': True}

    def call(self, method, params):
        core.require(method in code.RPC.METHODS, 'method is not read-only allowlisted')
        if method == 'eth_getBlockByNumber':
            core.require(params[0] in ('finalized', self.selected['number']) and params[1] is False,
                         'unexpected block selection')
            if params[0] == 'finalized':
                head = core.header(self.rpc.call(method, ['finalized', False]))
                core.require(core.quantity(head['number']) >= core.quantity(self.selected['number']),
                             'witness block is no longer finalized by this provider')
            result = self.rpc.call(method, [self.selected['number'], False])
            core.require(core.header(result) == self.selected, 'witness header changed during code collection')
            return result
        if method in ('eth_getCode', 'eth_getStorageAt', 'eth_call'):
            core.require(params[-1] == self.pin, 'code collector escaped witness block')
        return self.rpc.call(method, params)


def identity(report):
    # Compare the raw supported proxy evidence, not a claimed interpretation alone.
    return [{'address': n['address'].lower(), 'code': n['code'].lower(),
             'storage': {k: v.lower() for k, v in n['storage'].items()},
             'beacon': n.get('beacon')} for n in report['nodes']]


def assess(bundle):
    core.require(isinstance(bundle, dict) and set(bundle) == {'schema', 'codes', 'observations'}
                 and bundle['schema'] == SCHEMA, 'invalid witness context bundle')
    calls = witness.witness(bundle['observations'])
    codes = bundle['codes']
    core.require(isinstance(codes, list) and len(codes) == 2, 'two raw code observations required')
    for report, endpoint in zip(codes, core.ENDPOINTS):
        code.verify(report)
        origin = code.provenance(report)
        core.require(origin['transport_source'] == endpoint, 'code provider order or provenance mismatch')
        core.require(code.address(report['target']) == calls['call']['to'], 'code and call target differ')
        core.require(code.quantity(report['block']['number']) == core.quantity(calls['block']['number'])
                     and code.fixed_hex(report['block']['hash'], 32) == calls['block']['hash'],
                     'code and call blocks differ')
    same_code = identity(codes[0]) == identity(codes[1])
    verdict = ('disagree' if not same_code or calls['verdict'] == 'disagree' else calls['verdict'])
    return {'schema': 'witness-context-assessment-v1', 'chain_id': 1,
            'verdict': verdict, 'same_code_and_proxy_evidence': same_code,
            'block': calls['block'], 'block_number_decimal': core.quantity(calls['block']['number']),
            'target': calls['call']['to'], 'call_witness': calls,
            'code_providers': [{'source': code.provenance(r)['transport_source'],
                                'root_code_hash': r['nodes'][0]['code_hash'],
                                'candidate_effective_address': r['effective_address'],
                                'candidate_effective_code_hash': r['effective_code_hash'],
                                'opcode_inventory': opcodes.inspect(r)['nodes']} for r in codes],
            'limits': ['Two provider claims, not consensus proofs or proof of provider independence.',
                       'Same block and target permit reading code and call evidence together, not a safety verdict.',
                       'Proxy paths are candidates; opcode presence does not establish reachable execution.',
                       'Agree may include identical false returns or reverts; inspect execution statuses.',
                       'No gas, token movement, trace, state diff, receipt or future execution guarantee.']}


def load(path):
    with core.workspace_path(path).open('rb') as handle:
        raw = handle.read(LIMIT + 1)
    core.require(len(raw) <= LIMIT, 'bundle exceeds 98000 bytes')
    result = json.loads(raw, object_pairs_hook=witness.changes.no_duplicates,
                        parse_constant=witness.changes.reject_constant)
    assess(result)
    return result


def capture(tx, returns):
    observations = witness.capture_pair(tx, returns)
    selected = observations[0]['block']
    codes = [code.collect(PinnedCode(code.RPC(endpoint), selected), tx['to'])
             for endpoint in core.ENDPOINTS]
    bundle = {'schema': SCHEMA, 'codes': codes, 'observations': observations}
    assess(bundle)
    return bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    modes.add_parser('demo', help='offline real same-block ZTO code and call evidence')
    replay = modes.add_parser('replay')
    replay.add_argument('bundle')
    live = modes.add_parser('live', help='read-only ZTO totalSupply, or an explicit saved call')
    live.add_argument('--from-observation')
    live.add_argument('--save', help='new workspace file; limited to 98000 bytes')
    args = parser.parse_args(argv)
    try:
        if args.mode == 'demo':
            bundle = load(HERE / 'zto-context.json')
        elif args.mode == 'replay':
            bundle = load(args.bundle)
        else:
            destination = core.workspace_path(args.save) if args.save else None
            if destination:
                core.require(not destination.exists() and destination.parent.is_dir(),
                             'save requires a new file in an existing workspace directory')
            if args.from_observation:
                baseline = witness.changes.load_observation(args.from_observation)
                tx, returns = baseline['call'], baseline['returns']
            else:
                tx = {'to': core.TOKENS['ZTO'], 'data': '0x18160ddd', 'value': '0x0'}
                returns = 'uint256'
            bundle = capture(tx, returns)
            if destination:
                raw = (json.dumps(bundle, indent=2, allow_nan=False) + '\n').encode()
                core.require(len(raw) <= LIMIT, 'bundle exceeds 98000 bytes; not saved')
                with destination.open('xb') as handle:
                    handle.write(raw)
        result = assess(bundle)
        print(json.dumps(result, indent=2, allow_nan=False))
        return {'agree': 0, 'disagree': 1, 'inconclusive': 2}[result['verdict']]
    except (ValueError, KeyError, TypeError, OSError, RecursionError, core.RPCError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
