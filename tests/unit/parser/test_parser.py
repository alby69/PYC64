import unittest
from pyc64c.lexer import Lexer
from pyc64c.parser import Parser


class TestParser(unittest.TestCase):
    def test_parse_valid_program(self):
        code = "def main():\n    x: byte = 10\n"
        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(ast["k"], "Program")

    def test_parse_error_recovery(self):
        code = "def main(\n    x: byte = 10\n"
        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
        self.assertGreater(len(parser.errors), 0)
        self.assertEqual(parser.errors[0]["phase"], "parser")


if __name__ == "__main__":
    unittest.main()
