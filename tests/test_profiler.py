import unittest
import json
from pyc64c.compiler import compile_source
from pyc64c.engine import run_pipeline

class TestProfilerAndDiagnostics(unittest.TestCase):
    def test_estimated_cycles_returned(self):
        src = """
def main():
    print("test cycle counting")
"""
        # Run with simulate=True option
        res = run_pipeline(src, {"simulate": True})
        self.assertTrue(res.success)
        self.assertIn("estimated_cycles", res.metrics)
        self.assertTrue(res.metrics["estimated_cycles"] > 0)
        self.assertIn("estimated_frame_time", res.metrics)

    def test_structured_ai_diagnostics_syntax_error(self):
        # Trigger a syntax error
        src = "def main("
        res = run_pipeline(src)
        self.assertFalse(res.success)
        # Find the error diagnostic and check enriched fields
        errors = [d for d in res.diagnostics if d.get("severity") == "error"]
        self.assertTrue(len(errors) > 0)
        err = errors[0]
        self.assertIn("suggestion", err)
        self.assertEqual(err["fix_type"], "syntax_fix")
        self.assertEqual(err["confidence"], 0.85)

if __name__ == '__main__':
    unittest.main()
