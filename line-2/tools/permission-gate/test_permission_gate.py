"""Real ZTO replay and clearly synthetic edge cases; no RPC or wallets."""
import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch
import permission_gate as gate

REAL = gate.load(gate.HERE / 'live-observation.json')
DENY_ALL = gate.load(gate.HERE / 'demo-policy.json')


def permitted():
    result = copy.deepcopy(DENY_ALL)
    result['pairs'] = [{'owner': row['owner'], 'spender': row['spender'],
                        'maximum_allowance_raw': row['allowance_raw']}
                       for row in gate.changes.flatten(REAL)['pairs'].values()]
    return result


class GateTests(unittest.TestCase):
    def test_real_deny_all_exposes_three_permissions_including_empty_balances(self):
        result = gate.evaluate(REAL, DENY_ALL)
        self.assertEqual(result['decision'], 'deny')
        self.assertEqual(result['measured_pair_count'], 19)
        self.assertEqual(result['violating_pair_count'], 3)
        bad = [row for row in result['pairs'] if row['status'] != 'within_limit']
        self.assertEqual(sum(row['balance_raw'] == '0' for row in bad), 2)
        self.assertFalse(result['complete_wallet_audit'])

    def test_exact_real_limits_pass_only_measured_pairs(self):
        result = gate.evaluate(REAL, permitted())
        self.assertEqual(result['decision'], 'pass_measured_pairs')
        self.assertEqual(result['required_pair_count'], 19)

    def test_limit_one_unit_below_real_allowance_denies(self):
        value = permitted()
        item = next(p for p in value['pairs'] if int(p['maximum_allowance_raw']) > 0)
        item['maximum_allowance_raw'] = str(int(item['maximum_allowance_raw']) - 1)
        result = gate.evaluate(REAL, value)
        self.assertEqual(result['decision'], 'deny')
        self.assertEqual(result['violating_pair_count'], 1)
        self.assertIn('exceeds_limit', [r['status'] for r in result['pairs']])

    def test_missing_required_evidence_overrides_even_known_violation(self):
        partial = copy.deepcopy(REAL)
        partial['observations'].pop(0)
        value = permitted()
        for p in value['pairs']:
            p['maximum_allowance_raw'] = '0'
        result = gate.evaluate(partial, value)
        self.assertEqual(result['decision'], 'insufficient_evidence')
        self.assertGreater(result['missing_pair_count'], 0)
        self.assertEqual(result['violating_pair_count'], 3)
        self.assertTrue(any(r['allowance_raw'] is None for r in result['pairs']))

    def test_empty_real_event_scan_never_passes(self):
        empty = gate.load(gate.HERE.parent / 'allowance-changes' / 'lens-recheck.json')
        spec = copy.deepcopy(DENY_ALL)
        height = gate.changes.flatten(empty)['block_number']
        spec['minimum_block'] = spec['maximum_block'] = height
        result = gate.evaluate(empty, spec)
        self.assertEqual(result['decision'], 'insufficient_evidence')
        self.assertEqual(result['measured_pair_count'], 0)

    def test_block_interval_is_inclusive(self):
        for delta in (-1, 1):
            value = permitted()
            value['minimum_block'] += delta
            value['maximum_block'] += delta
            result = gate.evaluate(REAL, value)
            self.assertEqual(result['decision'], 'insufficient_evidence')
            self.assertFalse(result['policy_block_interval']['observed_in_interval'])

    def test_policy_token_mismatch_rejected(self):
        value = permitted()
        value['token_address'] = gate.lens.TOKENS['IMD']
        with self.assertRaisesRegex(ValueError, 'identity differ'):
            gate.evaluate(REAL, value)

    def test_nonethereum_chain_and_boolean_rejected(self):
        for chain in (True, '1', 2):
            value = permitted(); value['chain_id'] = chain
            with self.assertRaises(ValueError):
                gate.evaluate(REAL, value)

    def test_invalid_intervals_rejected(self):
        for low, high in ((True, 26184324), (0, False), (-1, 0), (2, 1), ('1', 2)):
            value = permitted(); value.update(minimum_block=low, maximum_block=high)
            with self.assertRaises(ValueError):
                gate.evaluate(REAL, value)

    def test_integer_precision_and_uint256_boundaries(self):
        for number in (0, 2**53+1, gate.lens.MAX_UINT):
            self.assertEqual(gate.raw_uint(str(number)), number)
        for value in ('01', '-1', '+1', '1.0', '1e18', '', 0, True, str(2**256)):
            with self.assertRaises(ValueError):
                gate.raw_uint(value)

    def test_case_normalized_duplicate_pairs_rejected(self):
        value = permitted()
        duplicate = copy.deepcopy(value['pairs'][0])
        duplicate['owner'] = '0x' + duplicate['owner'][2:].upper()
        value['pairs'].append(duplicate)
        with self.assertRaisesRegex(ValueError, 'duplicate policy pair'):
            gate.evaluate(REAL, value)

    def test_zero_address_rejected(self):
        value = permitted(); value['pairs'][0]['spender'] = '0x' + '0'*40
        with self.assertRaises(ValueError):
            gate.evaluate(REAL, value)

    def test_unknown_policy_fields_and_schema_rejected(self):
        for field, replacement in (('maximum_alowance', '0'), ('schema', 'other')):
            value = permitted(); value[field] = replacement
            with self.assertRaises(ValueError):
                gate.evaluate(REAL, value)
        value = permitted(); value['pairs'][0]['maximum_alowance_raw'] = '0'
        with self.assertRaises(ValueError):
            gate.evaluate(REAL, value)

    def test_oversized_policy_rejected(self):
        value = permitted(); value['pairs'] = value['pairs'] * 4
        with self.assertRaisesRegex(ValueError, 'at most 64'):
            gate.evaluate(REAL, value)

    def test_corrupt_evidence_is_rejected_not_a_policy_pass(self):
        value = copy.deepcopy(REAL)
        value['observations'][0]['raw']['allowances'][0]['data'] = '0x00'
        with self.assertRaises(ValueError):
            gate.evaluate(value, permitted())

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            json.loads('{"pairs":[],"pairs":[]}', object_pairs_hook=gate.unique_object)

    def test_demo_is_offline_and_matches_delivered_report(self):
        with patch.object(gate.lens, 'RPC', side_effect=AssertionError('network forbidden')):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(gate.main([]), 0)
        self.assertEqual(json.loads(output.getvalue()), gate.load(gate.HERE / 'example-report.json'))
        self.assertTrue(json.loads(output.getvalue())['demonstration'])

    def test_enforcement_exit_codes_and_json(self):
        for spec, expected in ((DENY_ALL, 3), (permitted(), 0)):
            with patch.object(gate, 'load', side_effect=[REAL, spec]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(gate.main(['--observation', 'input', '--policy', 'policy']), expected)
            self.assertFalse(json.loads(output.getvalue())['demonstration'])
        stale = permitted(); stale['maximum_block'] -= 1; stale['minimum_block'] -= 1
        with patch.object(gate, 'load', side_effect=[REAL, stale]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(gate.main(['--observation', 'input', '--policy', 'policy']), 4)

    def test_unpaired_arguments_are_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gate.main(['--policy', 'input']), 1)

    def test_workspace_path_rejects_external_input(self):
        with self.assertRaisesRegex(ValueError, 'inside the current workspace'):
            gate.load('/tmp/not-read.json')


if __name__ == '__main__':
    unittest.main()
