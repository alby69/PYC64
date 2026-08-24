import unittest
from pyc64c.exceptions import (
    PYC64Error, LexerError, ParseError, SemanticError,
    CodegenError, FixupError, SimulationError
)


class TestExceptions(unittest.TestCase):
    def test_pyc64_error_attributes(self):
        err = PYC64Error("Generic error", line=10, col=5, phase="engine", source_file="test.c64")
        self.assertEqual(err.message, "Generic error")
        self.assertEqual(err.line, 10)
        self.assertEqual(err.col, 5)
        self.assertEqual(err.phase, "engine")
        self.assertEqual(err.source_file, "test.c64")

        d = err.to_dict()
        self.assertEqual(d["message"], "Generic error")
        self.assertEqual(d["line"], 10)
        self.assertEqual(d["phase"], "engine")

        self.assertIn("[ENGINE]", str(err))
        self.assertIn("line 10", str(err))

    def test_lexer_error(self):
        err = LexerError("Unexpected char", line=2, col=3)
        self.assertEqual(err.phase, "lexer")
        self.assertEqual(err.message, "Unexpected char")
        self.assertIsInstance(err, PYC64Error)

    def test_parse_error(self):
        err = ParseError("Expected colon", line=4, col=1)
        self.assertEqual(err.phase, "parser")
        self.assertIsInstance(err, PYC64Error)

    def test_other_errors(self):
        self.assertEqual(SemanticError("msg").phase, "semantic")
        self.assertEqual(CodegenError("msg").phase, "codegen")
        self.assertEqual(FixupError("msg").phase, "fixup")
        self.assertEqual(SimulationError("msg").phase, "simulation")


if __name__ == "__main__":
    unittest.main()
