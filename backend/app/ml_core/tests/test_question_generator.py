import unittest
import sys, os
# Ensure src is importable when running tests directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from chains.question_generator import get_exam_chain

class TestQuestionGeneratorFallback(unittest.TestCase):
    def test_subjective_fallback(self):
        chain = get_exam_chain(question_type='subjective')
        self.assertIsNotNone(chain)
        resp = chain.invoke({'topic':'Work and Energy','difficulty':'Easy'})
        self.assertIn('**Question:**', resp)
        self.assertIn('**Answer Key:**', resp)

    def test_mcq_fallback(self):
        chain = get_exam_chain(question_type='mcq')
        self.assertIsNotNone(chain)
        resp = chain.invoke({'topic':'Gravity','difficulty':'Medium'})
        self.assertIn('**Question:**', resp)
        self.assertIn('**Options:**', resp)
        self.assertIn('**Correct Answer:**', resp)

if __name__ == '__main__':
    unittest.main()
