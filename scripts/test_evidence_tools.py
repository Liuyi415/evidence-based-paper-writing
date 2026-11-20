"""Synthetic boundary tests; these are not research experiments."""
import copy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import evidence_tools as et


class EvidenceChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.root = self.work / 'sources'
        self.root.mkdir()
        (self.root / 'results.csv').write_text('model,score\nA,0.80\nB,0.84\n', encoding='utf-8')
        (self.root / 'notes.md').write_text('Synthetic data only.\nOne run.\n', encoding='utf-8')
        (self.root / 'summary.json').write_text('{"metrics":{"score":0.84},"test_accessed":false}', encoding='utf-8')
        self.manifest = self.work / 'manifest.json'
        et.inventory(self.root, self.manifest)
        self.data = {
            'evidence': [
                {'id': 'E001', 'path': 'results.csv', 'kind': 'csv', 'row': 1, 'column': 'score', 'value': '0.80'},
                {'id': 'E002', 'path': 'results.csv', 'kind': 'csv', 'row': 2, 'column': 'score', 'value': '0.84'},
                {'id': 'E003', 'path': 'notes.md', 'kind': 'text', 'line_start': 1, 'line_end': 1, 'quote': 'Synthetic data only.'},
                {'id': 'E004', 'path': 'summary.json', 'kind': 'json', 'pointer': '/metrics/score', 'value': '0.84'},
                {'id': 'E005', 'path': 'summary.json', 'kind': 'json', 'pointer': '/test_accessed', 'value': False},
            ],
            'claims': [{'id': 'C001', 'text': 'Synthetic change is 5%.', 'status': 'observed',
                        'evidence_ids': ['E001', 'E002', 'E003', 'E004', 'E005'],
                        'calculation': {'operation': 'relative_change_percent', 'inputs': ['E001', 'E002'],
                                        'expected': '5', 'tolerance': '0'}}]}
        self.evidence = self.work / 'evidence.json'
        self.draft = self.work / 'draft.md'
        self.draft.write_text('Synthetic change is 5%. [[C001]]\n', encoding='utf-8')

    def run_check(self):
        et.write_json(self.evidence, self.data)
        return et.check(self.root, self.manifest, self.evidence, self.draft)

    def test_valid_numeric_text_and_json(self):
        result = self.run_check()
        self.assertTrue(result['mechanical_pass'], result['errors'])
        self.assertEqual(result['verified_calculations'][0]['actual'], '5.00')

    def test_source_drift(self):
        (self.root / 'notes.md').write_text('Synthetic data only.\nTwo runs.\n', encoding='utf-8')
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_wrong_csv_value(self):
        self.data['evidence'][0]['value'] = '0.9'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_wrong_calculation(self):
        self.data['claims'][0]['calculation']['expected'] = '4'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_wrong_quote(self):
        self.data['evidence'][2]['quote'] = 'Never observed.'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_wrong_line_range(self):
        self.data['evidence'][2]['line_start'] = 2
        self.data['evidence'][2]['line_end'] = 2
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_missing_evidence(self):
        self.data['claims'][0]['evidence_ids'].append('E999')
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_duplicate_evidence(self):
        self.data['evidence'].append(copy.deepcopy(self.data['evidence'][0]))
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_unknown_draft_marker(self):
        self.draft.write_text('Synthetic change is 5%. [[C001]]\nUnknown [[C999]]', encoding='utf-8')
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_claim_text_not_next_to_marker(self):
        self.draft.write_text('Synthetic change is 5%.\nOther content. [[C001]]', encoding='utf-8')
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_empty_claim_set(self):
        self.data['claims'] = []
        with self.assertRaisesRegex(et.EvidenceError, 'no claims'):
            self.run_check()

    def test_path_traversal(self):
        with self.assertRaises(et.EvidenceError):
            et.safe_source(self.root, '../notes.md')

    def test_output_cannot_modify_sources(self):
        before = (self.root / 'results.csv').read_bytes()
        with contextlib.redirect_stderr(io.StringIO()):
            code = et.main(['inventory', '--sources-root', str(self.root), '--out', str(self.root / 'results.csv')])
        self.assertEqual(code, 1)
        self.assertEqual(before, (self.root / 'results.csv').read_bytes())

    def test_zero_denominator(self):
        (self.root / 'results.csv').write_text('model,score\nA,0\nB,0.84\n', encoding='utf-8')
        et.inventory(self.root, self.manifest)
        self.data['evidence'][0]['value'] = '0'
        result = self.run_check()
        self.assertFalse(result['mechanical_pass'])
        self.assertTrue(any('zero baseline' in e for e in result['errors']))

    def test_nonfinite_rejected(self):
        self.data['evidence'][0]['value'] = 'NaN'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_duplicate_json_keys_rejected(self):
        (self.root / 'summary.json').write_text('{"score":0.84,"score":0.85}', encoding='utf-8')
        et.inventory(self.root, self.manifest)
        self.data['evidence'][3]['pointer'] = '/score'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_json_boolean_is_not_numeric(self):
        self.data['evidence'][4]['value'] = 0
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_bad_json_pointer(self):
        self.data['evidence'][3]['pointer'] = '/metrics/nonexistent'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_duplicate_csv_headers(self):
        (self.root / 'results.csv').write_text('score,score\n0.80,0.80\n0.84,0.84\n', encoding='utf-8')
        et.inventory(self.root, self.manifest)
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_negative_tolerance(self):
        self.data['claims'][0]['calculation']['tolerance'] = '-1'
        self.assertFalse(self.run_check()['mechanical_pass'])

    def test_malformed_input_cli_writes_failure(self):
        self.evidence.write_text('{bad', encoding='utf-8')
        output = self.work / 'verification.json'
        with contextlib.redirect_stdout(io.StringIO()):
            code = et.main(['check', '--sources-root', str(self.root), '--manifest', str(self.manifest),
                            '--evidence', str(self.evidence), '--draft', str(self.draft), '--out', str(output)])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(output.read_text(encoding='utf-8'))['mechanical_pass'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
