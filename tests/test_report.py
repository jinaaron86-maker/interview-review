import importlib.util
import os
import sys
import unittest
from pathlib import Path

module_path = os.environ.get('REVIEW_MODULE', str(Path(__file__).parents[1] / 'scripts/report.py'))
sys.path.insert(0, str(Path(module_path).parent))
spec = importlib.util.spec_from_file_location('report', module_path)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

class EvidenceTests(unittest.TestCase):
    def test_absent_score_does_not_imply_pass(self):
        self.assertEqual(report.question_view({'observed_answer': '未提供'})['score'], '未评分：证据不足')

    def test_explicit_unscored_remains_unscored(self):
        self.assertEqual(report.question_view({'score': None})['score'], '未评分：证据不足')

    def test_valid_score_is_preserved(self):
        self.assertEqual(report.question_view({'score': 4})['score'], '4/5')

if __name__ == '__main__':
    unittest.main()
