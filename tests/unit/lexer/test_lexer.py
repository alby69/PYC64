import unittest
from pyc64c.lexer import Lexer
from pyc64c.token_types import TT


class TestLexer(unittest.TestCase):
    def test_indent_dedent(self):
        code = "def main():\n    x: byte = 1\n"
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        types = [t.type for t in tokens]
        self.assertIn(TT.INDENT, types)
        self.assertIn(TT.DEDENT, types)

    def test_hex_literal(self):
        code = "x: word = $D020\ny: word = 0x0801"
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        hex_tokens = [t for t in tokens if t.type == TT.HEX_LIT]
        self.assertEqual(len(hex_tokens), 2)
        self.assertEqual(hex_tokens[0].value, 0xD020)
        self.assertEqual(hex_tokens[1].value, 0x0801)

    def test_invalid_char(self):
        code = "var @ bad"
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0]["phase"], "lexer")
        self.assertEqual(errors[0]["line"], 1)


if __name__ == "__main__":
    unittest.main()
