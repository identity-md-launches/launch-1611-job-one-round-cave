#!/usr/bin/env python3
"""Compare independent ZTO/IMD trade sizes against one real pool snapshot."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'zto-path'))
import zto_path as path

DEFAULT_SNAPSHOT = Path(__file__).resolve().parent.parent / 'zto-path' / 'observation.json'
MAX_CANDIDATES = 20


def bps(value, label):
    path.z.require(type(value) is int and 0 <= value < 10000,
                   label + ' must be an integer in 0..9999')
    return value


def ceiling(value):
    return -(-value.numerator // value.denominator)


def compare_sizes(observation, amounts, token, slippage_bps, max_loss_bps=None):
    """Candidates are separate hypothetical swaps, never sequential pool mutations.

    The loss baseline is the initial raw spot ratio * gross input. It includes
    fees, curve movement and integer rounding. It is NOT slippage or a price
    from an external market. A loss ceiling is compared as an exact rational.
    """
    bps(slippage_bps, 'slippage bps')
    if max_loss_bps is not None:
        bps(max_loss_bps, 'maximum spot loss bps')
    path.z.require(token in ('ZTO', 'IMD'), 'input must be ZTO or IMD')
    path.z.require(isinstance(amounts, (list, tuple)) and 1 <= len(amounts) <= MAX_CANDIDATES,
                   'supply 1..20 independent candidate amounts')
    path.z.require(all(isinstance(a, str) and len(a) <= 100 for a in amounts),
                   'each amount must be a decimal string of at most 100 characters')
    state, _, _ = path.decode(observation)
    # token0=IMD, token1=ZTO. Use raw units; no decimal or float conversion.
    price_squared = state['price'] ** 2
    spot = (Fraction(price_squared, 1 << 192) if token == 'IMD'
            else Fraction(1 << 192, price_squared))
    dout = state['decimals'][1] if token == 'IMD' else state['decimals'][0]
    rows = []
    for amount in amounts:
        quote = path.quote(observation, token, amount)
        row = {'amount': amount, 'requested_input_raw': quote['requested_input_raw'],
               'pool_status': quote['status'],
               'initialized_ticks_crossed': quote['initialized_ticks_crossed']}
        if quote['status'] != 'estimated':
            row.update(status='incomplete', partial=quote['partial'])
        else:
            estimate = quote['estimate']
            output = int(estimate['output_raw'])
            baseline = int(quote['requested_input_raw']) * spot
            loss = (1 - Fraction(output, 1) / baseline) * 10000
            minimum = output * (10000-slippage_bps) // 10000
            row.update(estimate=estimate,
                       gross_spot_output_raw={'numerator': str(baseline.numerator),
                                              'denominator': str(baseline.denominator)},
                       spot_loss_bps={'numerator': str(loss.numerator),
                                      'denominator': str(loss.denominator),
                                      'ceiling': ceiling(loss)})
            if output == 0 or minimum == 0:
                row.update(status='zero_output_bound',
                           reason='Output or rounded minimum is zero; no usable output bound.')
            elif max_loss_bps is not None and loss > max_loss_bps:
                row.update(status='above_loss_limit',
                           reason='Fee-inclusive spot loss exceeds the chosen maximum.')
            else:
                row.update(status='candidate', minimum_output_raw=str(minimum),
                           minimum_output=path.z.units(minimum, dout))
        rows.append(row)
    usable = [r for r in rows if r['status'] == 'candidate']
    largest = max(usable, key=lambda r: int(r['requested_input_raw'])) if usable else None
    return {'schema': 'zto-sizes-report-v1', 'chain_id': 1, 'pool_id': path.z.POOL,
            'block': observation['base']['block'], 'source': observation['base']['source'],
            'input_token': token, 'output_token': 'IMD' if token == 'ZTO' else 'ZTO',
            'slippage_bps': slippage_bps, 'max_spot_loss_bps': max_loss_bps,
            'candidate_count': len(usable),
            'largest_candidate_input_raw': largest['requested_input_raw'] if largest else None,
            'minimum_rounding': 'floor(estimated_output_raw * (10000 - slippage_bps) / 10000)',
            'scope': 'Independent candidate sizes at one observed block; no trade recommendation.',
            'limitations': ['Historical snapshot is not a current quote or freshness guarantee.',
                            'Minimum is a planning number, not an enforced or guaranteed receipt.',
                            'Spot loss includes fees and rounding; it is separate from slippage tolerance.',
                            'No router calldata, settlement, transfer behavior, gas or MEV simulation.',
                            'Largest candidate means largest supplied amount passing the chosen filters, not pool capacity.'],
            'candidates': rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default=str(DEFAULT_SNAPSHOT),
                        help='workspace ZTO Path snapshot; default is the bundled historical observation')
    parser.add_argument('--input', choices=('ZTO', 'IMD'), default='ZTO')
    parser.add_argument('--amount', action='append', required=True,
                        help='positive token amount; repeat for up to 20 independent candidates')
    parser.add_argument('--slippage-bps', type=int, required=True,
                        help='explicit planning tolerance, integer 0..9999')
    parser.add_argument('--max-spot-loss-bps', type=int,
                        help='optional fee-inclusive loss filter, integer 0..9999')
    args = parser.parse_args(argv)
    try:
        result = compare_sizes(path.read_json(args.snapshot), args.amount, args.input,
                               args.slippage_bps, args.max_spot_loss_bps)
        print(json.dumps(result, indent=2))
        return 0 if result['candidate_count'] else 2
    except (ValueError, KeyError, TypeError, AttributeError, OSError, OverflowError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
