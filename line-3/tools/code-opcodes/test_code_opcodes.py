import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import code_opcodes as tool

ROOT = Path(__file__).resolve().parents[1] / 'code-lens'


class CodeOpcodesTests(unittest.TestCase):
    def report(self, token):
        return json.loads((ROOT / (token + '-observation.json')).read_text())

    def test_real_zto(self):
        result = tool.inspect(self.report('zto'))
        self.assertEqual(result['target'], tool.lens.ZTO)
        self.assertEqual(result['nodes'][0]['recognized_solidity_metadata']['solc_version'], '0.8.26')
        self.assertEqual(result['nodes'][0]['delegation_opcode_offsets'], [])

    def test_real_imd_metadata_is_not_executable_callcode(self):
        result = tool.inspect(self.report('imd'))
        node = result['nodes'][0]
        self.assertEqual(node['recognized_solidity_metadata']['solc_version'], '0.8.26')
        self.assertEqual(node['delegation_opcode_offsets'], [])
        self.assertEqual([x['opcode'] for x in node['findings']], ['EXTCODESIZE'] * 4)

    def test_push_data_is_skipped_and_actual_delegatecall_is_found(self):
        metadata, findings = tool.scan(bytes.fromhex('60f47ff2') + bytes(31) + bytes.fromhex('f4'))
        self.assertIsNone(metadata)
        self.assertEqual(findings, [{'offset': 35, 'opcode': 'DELEGATECALL'}])

    def test_unrecognized_tail_is_scanned(self):
        metadata, findings = tool.scan(bytes.fromhex('f2ff0000'))
        self.assertIsNone(metadata)
        self.assertEqual([x['opcode'] for x in findings], ['CALLCODE', 'SELFDESTRUCT'])

    def test_tampered_report_is_rejected(self):
        report = copy.deepcopy(self.report('zto'))
        report['nodes'][0]['code'] = '0xf4'
        with self.assertRaises(ValueError):
            tool.inspect(report)

    def test_unresolved_signal_for_actual_delegation(self):
        report = copy.deepcopy(self.report('zto'))
        node = report['nodes'][0]
        original = bytes.fromhex(node['code'][2:])
        start = tool.solidity_metadata(original)['start']
        raw = original[:start] + b'\xf4' + original[start:]
        node['code'] = '0x' + raw.hex()
        node['code_bytes'] = len(raw)
        node['code_hash'] = tool.lens.digest(raw)
        report['effective_code_hash'] = node['code_hash']
        result = tool.inspect(report)
        self.assertTrue(result['nodes'][0]['unresolved_delegation_signal'])
        self.assertEqual(result['nodes'][0]['delegation_opcode_offsets'], [start])
        self.assertEqual(result['nodes'][0]['recognized_solidity_metadata']['start'], start + 1)


if __name__ == '__main__':
    unittest.main()
