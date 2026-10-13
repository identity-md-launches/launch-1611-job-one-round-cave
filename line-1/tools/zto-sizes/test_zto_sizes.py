"""Real-state and integer-bound regressions; no network required."""
import contextlib
from fractions import Fraction
import io
import json
import unittest
from unittest.mock import patch

import zto_sizes as s


class SizesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = s.path.read_json(str(s.DEFAULT_SNAPSHOT))

    def report(self, amounts, token='ZTO', slip=100, loss=None):
        return s.compare_sizes(self.obs, amounts, token, slip, loss)

    def test_replays_all_real_quoter_outputs(self):
        evidence = s.path.read_json(str(s.DEFAULT_SNAPSHOT.parent / 'quoter-check.json'))
        for case in evidence['results']:
            r = self.report([case['amount']], case['input_token'])['candidates'][0]
            self.assertEqual(r['estimate']['output_raw'],
                             str(s.path.z.words(case['raw_result'], 2)[0]))

    def test_integer_minimum_for_large_real_output(self):
        r = self.report(['100000000'])['candidates'][0]
        self.assertEqual(r['estimate']['output'], '1196.130391948897309582')
        self.assertEqual(r['minimum_output_raw'], '1184169088029408336486')
        output = int(r['estimate']['output_raw'])
        minimum = int(r['minimum_output_raw'])
        # Floor bounds without reusing the implementation's calculation.
        self.assertLessEqual(minimum * 10000, output * 9900)
        self.assertGreater((minimum + 1) * 10000, output * 9900)

    def test_partial_fill_never_has_minimum(self):
        r = self.report(['1', '1000000000'])
        partial = r['candidates'][1]
        self.assertEqual(partial['status'], 'incomplete')
        self.assertNotIn('minimum_output_raw', partial)
        self.assertNotIn('estimate', partial)
        self.assertGreater(int(partial['partial']['input_unspent_raw']), 0)
        self.assertEqual(r['candidate_count'], 1)

    def test_zero_outputs_never_become_candidates(self):
        for token in ('ZTO', 'IMD'):
            r = self.report(['0.000000000000000001'], token)
            self.assertEqual(r['candidate_count'], 0)
            self.assertEqual(r['candidates'][0]['status'], 'zero_output_bound')
            self.assertNotIn('minimum_output_raw', r['candidates'][0])

    def test_reverse_spot_ratio_and_decimals(self):
        for token in ('ZTO', 'IMD'):
            r = self.report(['1'], token)['candidates'][0]
            baseline = r['gross_spot_output_raw']
            raw = Fraction(int(baseline['numerator']), int(baseline['denominator']))
            price = s.path.decode(self.obs)[0]['price']
            expected = (Fraction(price*price, 1 << 192) if token == 'IMD'
                        else Fraction(1 << 192, price*price)) * 10**18
            self.assertEqual(raw, expected)
            self.assertEqual(r['minimum_output'],
                             s.path.z.units(int(r['minimum_output_raw']), 18))

    def test_loss_threshold_exact_rational(self):
        r = self.report(['1'])['candidates'][0]
        loss = r['spot_loss_bps']
        exact = Fraction(int(loss['numerator']), int(loss['denominator']))
        upper = loss['ceiling']
        self.assertTrue(upper - 1 < exact <= upper)
        self.assertEqual(self.report(['1'], loss=upper)['candidate_count'], 1)
        fail = self.report(['1'], loss=upper-1)['candidates'][0]
        self.assertEqual(fail['status'], 'above_loss_limit')
        self.assertNotIn('minimum_output_raw', fail)

    def test_zero_tolerance_and_extreme_tolerance(self):
        zero = self.report(['1'], slip=0)['candidates'][0]
        self.assertEqual(zero['minimum_output_raw'], zero['estimate']['output_raw'])
        high = self.report(['1'], slip=9999)['candidates'][0]
        self.assertLess(int(high['minimum_output_raw']), int(zero['minimum_output_raw']))

    def test_unsorted_candidates_are_independent(self):
        amounts = ['1000', '1', '100000000', '1000']
        r = self.report(amounts)
        self.assertEqual([a['amount'] for a in r['candidates']], amounts)
        self.assertEqual(r['largest_candidate_input_raw'], str(10**26))
        for row in r['candidates']:
            self.assertEqual(row, self.report([row['amount']])['candidates'][0])

    def test_invalid_settings_and_inputs(self):
        for value in (-1, 10000, True, '100', 1.5):
            with self.assertRaises(ValueError): self.report(['1'], slip=value)
            with self.assertRaises(ValueError): self.report(['1'], loss=value)
        for amounts in ([], ['1'] * 21, [1], ['9'*101], ['0'], ['-1'], ['1e6'],
                        ['0.0000000000000000001']):
            with self.assertRaises(ValueError): self.report(amounts)
        with self.assertRaises(ValueError): self.report(['1'], token='OTHER')

    def test_no_usable_candidate_has_no_largest(self):
        r = self.report(['1000000000'])
        self.assertIsNone(r['largest_candidate_input_raw'])
        self.assertEqual(r['candidate_count'], 0)

    def test_cli_offline_and_exit_codes(self):
        with patch.object(s.path.z, 'RPC', side_effect=AssertionError('network forbidden')):
            for amount, code in [('1', 0), ('1000000000', 2)]:
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(s.main(['--amount', amount, '--slippage-bps', '100']), code)
                self.assertEqual(json.loads(out.getvalue())['schema'], 'zto-sizes-report-v1')
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(s.main(['--amount', '0', '--slippage-bps', '100']), 1)
            self.assertIn('error', json.loads(err.getvalue()))

    def test_wrong_pool_snapshot_refused(self):
        import copy
        observation = copy.deepcopy(self.obs)
        observation['base']['initialize']['topics'][1] = '0x' + '11' * 32
        with self.assertRaises(ValueError):
            s.compare_sizes(observation, ['1'], 'ZTO', 100)


if __name__ == '__main__':
    unittest.main()
