"""Real raw evidence replay; mutated branches below are explicitly synthetic."""
import copy
import json
import unittest
import witness_context as tool


class ContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = tool.load(tool.HERE / 'zto-context.json')

    def test_real_context_agrees_at_exact_block(self):
        result = tool.assess(self.real)
        self.assertEqual(result['verdict'], 'agree')
        self.assertTrue(result['same_code_and_proxy_evidence'])
        self.assertEqual(result['block_number_decimal'], int(self.real['observations'][0]['block']['number'], 16))
        self.assertEqual(len(result['code_providers']), 2)
        self.assertEqual(result['call_witness']['providers'][0]['result']['uint256'], '1000000000000000000000000000')

    def test_code_disagreement_never_becomes_agreement(self):
        bundle = copy.deepcopy(self.real)
        report = bundle['codes'][1]
        node = report['nodes'][0]
        node['code'] = '0x60006000'
        node['code_bytes'] = 4
        node['code_hash'] = tool.code.digest(bytes.fromhex('60006000'))
        report['effective_code_hash'] = node['code_hash']
        self.assertEqual(tool.assess(bundle)['verdict'], 'disagree')

    def test_call_disagreement_never_becomes_agreement(self):
        bundle = copy.deepcopy(self.real)
        bundle['observations'][1]['outcome']['result'] = '0x' + format(1, '064x')
        self.assertEqual(tool.assess(bundle)['verdict'], 'disagree')

    def test_matching_false_returns_are_only_agreement(self):
        bundle = copy.deepcopy(self.real)
        for observation in bundle['observations']:
            observation['returns'] = 'bool'
            observation['outcome'] = {'result': '0x' + format(0, '064x')}
        result = tool.assess(bundle)
        self.assertEqual(result['verdict'], 'agree')
        self.assertEqual(result['call_witness']['providers'][0]['result']['status'], 'returned_false')

    def test_incomplete_call_stays_inconclusive(self):
        bundle = copy.deepcopy(self.real)
        bundle['observations'][1]['outcome']['result'] = '0x'
        self.assertEqual(tool.assess(bundle)['verdict'], 'inconclusive')

    def test_code_block_target_and_provenance_mismatches_rejected(self):
        for mutation in ('height', 'hash', 'target', 'provider'):
            bundle = copy.deepcopy(self.real)
            report = bundle['codes'][1]
            if mutation == 'height':
                report['block']['number'] = hex(int(report['block']['number'], 16) + 1)
            elif mutation == 'hash':
                report['block']['hash'] = '0x' + 'ab' * 32
            elif mutation == 'target':
                report['target'] = tool.code.IMD
                report['nodes'][0]['address'] = tool.code.IMD
                report['effective_address'] = tool.code.IMD
            else:
                report['source'] = report['transport_source'] = tool.core.ENDPOINTS[0]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                tool.assess(bundle)

    def test_tampered_runtime_rejected(self):
        bundle = copy.deepcopy(self.real)
        bundle['codes'][0]['nodes'][0]['code'] = '0x6000'
        with self.assertRaises(ValueError):
            tool.assess(bundle)

    def test_duplicate_providers_rejected(self):
        bundle = copy.deepcopy(self.real)
        bundle['observations'][1]['source'] = bundle['observations'][0]['source']
        with self.assertRaises(ValueError):
            tool.assess(bundle)

    def test_assessment_does_not_mutate_evidence(self):
        original = copy.deepcopy(self.real)
        tool.assess(self.real)
        self.assertEqual(self.real, original)

    def test_pin_adapter_rejects_escape_and_wrong_header(self):
        block = self.real['observations'][0]['block']
        class FakeRPC:
            endpoint = tool.core.ENDPOINTS[0]
            def call(self, method, params):
                return dict(block, number=hex(int(block['number'], 16) + 1))
        session = tool.PinnedCode(FakeRPC(), block)
        with self.assertRaisesRegex(ValueError, 'escaped'):
            session.call('eth_getCode', [tool.code.ZTO, 'latest'])
        with self.assertRaisesRegex(ValueError, 'header changed'):
            session.call('eth_getBlockByNumber', [block['number'], False])
        with self.assertRaisesRegex(ValueError, 'allowlisted'):
            session.call('eth_sendRawTransaction', [])

    def test_workspace_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, 'workspace'):
            tool.load('../outside.json')


if __name__ == '__main__':
    unittest.main()
