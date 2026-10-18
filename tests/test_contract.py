import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import report

PLAN = json.loads((Path(__file__).parents[1] / 'examples/review_plan.json').read_text(encoding='utf-8'))

class ContractTests(unittest.TestCase):
    def test_unknown_fields_cannot_leak_into_delivery(self):
        plan = copy.deepcopy(PLAN)
        plan['passing_probability'] = '65%'
        self.assertTrue(report.validate(plan))

    def test_missing_jd_requires_partial(self):
        plan = copy.deepcopy(PLAN)
        plan['inputs']['jd'] = False
        self.assertTrue(report.validate(plan))
        plan['mode'] = 'partial'
        self.assertEqual(report.validate(plan), [])

    def test_unverified_answer_cannot_be_scored(self):
        plan = copy.deepcopy(PLAN)
        plan['questions'][2]['score'] = 3
        self.assertTrue(report.validate(plan))

    def test_no_record_cannot_be_presented_as_retrospective(self):
        plan = copy.deepcopy(PLAN)
        plan['transcript_markdown'] = ''
        self.assertTrue(report.validate(plan))


    def test_edited_answers_cannot_replace_verbatim_evidence(self):
        plan = copy.deepcopy(PLAN)
        plan['qa_transcript'][0]['answer_verbatim'] = '这是优化后编造的回答。'
        self.assertTrue(report.validate(plan))
