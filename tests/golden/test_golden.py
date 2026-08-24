import os
import glob
import hashlib
import unittest
from pyc64c.compiler import compile_to_prg


class TestGoldenSnapshots(unittest.TestCase):
    def test_example_compilations(self):
        c64_files = sorted(glob.glob("examples/*.c64") + glob.glob("*.c64"))
        self.assertGreater(len(c64_files), 0, "No .c64 example files found for golden testing")

        compiled_count = 0
        for filepath in c64_files:
            with open(filepath, "r", encoding="utf-8") as f:
                src = f.read()

            prg, res = compile_to_prg(src)
            self.assertTrue(
                res.success,
                f"Failed to compile golden example {filepath}: {res.lex_errors + res.parse_errors}"
            )
            self.assertIsNotNone(prg, f"PRG output was None for {filepath}")
            self.assertGreater(len(prg), 2, f"PRG output too small for {filepath}")

            # Verify C64 PRG header standard (0x01, 0x08 for $0801)
            self.assertEqual(prg[0], 0x01)
            self.assertEqual(prg[1], 0x08)

            compiled_count += 1

        self.assertGreaterEqual(compiled_count, 5)


if __name__ == "__main__":
    unittest.main()
