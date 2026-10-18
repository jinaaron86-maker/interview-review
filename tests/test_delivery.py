import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
PLAN = json.loads((ROOT / 'examples/review_plan.json').read_text(encoding='utf-8'))

class DeliveryTests(unittest.TestCase):
    def run_plan(self, plan, base, extra=(), env=None):
        source = base / 'plan.json'
        source.write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
        out = base / 'report'
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/report.py'), '--plan', str(source), '--out', str(out), *extra], capture_output=True, text=True, env=env)
        return result, out

    def test_partial_delivers_editable_evidence_without_inventing_time(self):
        with tempfile.TemporaryDirectory() as folder:
            plan = copy.deepcopy(PLAN)
            plan['mode'] = 'partial'
            plan['inputs'].update(jd=False, resume=False)
            plan['limitations'] = '缺简历和JD，不核验经历一致性、不评价岗位匹配度。'
            result, out = self.run_plan(plan, Path(folder))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((out / '_support/transcript_timestamped.md').read_text(encoding='utf-8'), plan['transcript_markdown'])
            text = (out / '_support/interview_review.md').read_text(encoding='utf-8')
            self.assertIn('未评分：证据不足', text)
            self.assertNotIn('00:00', text)

    def test_rerun_does_not_overwrite_previous_work(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            _, out = self.run_plan(PLAN, base)
            before = {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()}
            result, _ = self.run_plan(PLAN, base)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()})

    def test_missing_pdf_tool_still_delivers_markdown_with_explicit_status(self):
        with tempfile.TemporaryDirectory() as folder:
            env = {**os.environ, 'PATH': ''}
            result, out = self.run_plan(PLAN, Path(folder), env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((out / '_support/interview_review.md').exists())
            self.assertFalse((out / 'interview_review.pdf').exists())
            quality = json.loads((out / '_support/quality_report.json').read_text(encoding='utf-8'))
            self.assertIn('缺少xelatex', quality['pdf'])
            self.assertEqual(quality['delivery_status'], 'incomplete')

    def test_two_pdf_files_are_the_only_formal_deliverables(self):
        import shutil
        if not shutil.which('xelatex'):
            self.skipTest('PDF compiler not available')
        with tempfile.TemporaryDirectory() as folder:
            result, out = self.run_plan(PLAN, Path(folder))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({p.name for p in out.iterdir() if p.is_file()}, {'interview_review.pdf', 'question_transcript.pdf'})
