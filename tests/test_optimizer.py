import unittest
from pyc64c.compiler import compile_source
from pyc64c.optimizer import optimize_ast

class TestOptimizer(unittest.TestCase):
    def test_unused_global_pruned(self):
        # x is unused, so it should be pruned. y is used, so it should remain.
        src = """
x: byte = 10
y: byte = 20
def main():
    print(y)
"""
        res = compile_source(src)
        self.assertTrue(res.success)
        # Check that x is NOT in globals, but y is
        globals_list = res.ast.get('globals', [])
        global_names = [g['name'] for g in globals_list]
        self.assertNotIn('x', global_names)
        self.assertIn('y', global_names)

    def test_unused_function_pruned(self):
        # unused_func is never called, so it should be pruned.
        src = """
def unused_func():
    print("unused")

def main():
    print("hello")
"""
        res = compile_source(src)
        self.assertTrue(res.success)
        funcs_list = res.ast.get('funcs', [])
        func_names = [f['name'] for f in funcs_list]
        self.assertNotIn('unused_func', func_names)
        self.assertIn('main', func_names)

    def test_unused_local_variable_pruned(self):
        # local x is unused, so it should be pruned from main's body.
        src = """
def main():
    x: byte = 42
    y: byte = 10
    print(y)
"""
        res = compile_source(src)
        self.assertTrue(res.success)
        # Locate local declarations in main's body
        main_func = [f for f in res.ast.get('funcs', []) if f['name'] == 'main'][0]
        stmts = main_func['body']['stmts']
        local_decls = [s['name'] for s in stmts if s.get('k') == 'VarDecl']
        self.assertNotIn('x', local_decls)
        self.assertIn('y', local_decls)

    def test_unused_local_variable_with_side_effect_kept(self):
        # x's declaration is pruned but its initializer (the function call) is preserved as an ExprStmt
        src = """
def foo():
    return 1

def main():
    x: byte = foo()
"""
        res = compile_source(src)
        self.assertTrue(res.success)
        main_func = [f for f in res.ast.get('funcs', []) if f['name'] == 'main'][0]
        stmts = main_func['body']['stmts']
        self.assertTrue(any(s.get('k') == 'ExprStmt' and s['expr']['k'] == 'Call' and s['expr']['name'] == 'foo' for s in stmts))

    def test_dead_if_blocks_pruned(self):
        # if False block should be pruned entirely
        src = """
def main():
    if 10 < 5:
        print("dead")
    else:
        print("alive")
"""
        res = compile_source(src)
        self.assertTrue(res.success)
        main_func = [f for f in res.ast.get('funcs', []) if f['name'] == 'main'][0]
        stmts = main_func['body']['stmts']
        # The statement list should just contain print("alive") directly, and NO 'If' statement!
        self.assertFalse(any(s.get('k') == 'If' for s in stmts))
        self.assertTrue(any(s.get('k') == 'ExprStmt' and s['expr']['k'] == 'Call' and s['expr']['args'][0]['value'] == 'alive' for s in stmts))

    def test_loop_unrolling_small(self):
        src = """
def main():
    for i in range(0, 3):
        print(i)
"""
        res = compile_source(src)
        self.assertTrue(res.success)
        main_func = [f for f in res.ast.get('funcs', []) if f['name'] == 'main'][0]
        stmts = main_func['body']['stmts']

        # There should be NO 'For' statement in stmts!
        self.assertFalse(any(s.get('k') == 'For' for s in stmts))

        # There should be 3 assignments to i (i = 0, i = 1, i = 2) and 3 print(i) calls
        assignments = [s for s in stmts if s.get('k') == 'Assign' and s['target']['name'] == 'i']
        self.assertEqual(len(assignments), 3)
        self.assertEqual(assignments[0]['value']['value'], 0)
        self.assertEqual(assignments[1]['value']['value'], 1)
        self.assertEqual(assignments[2]['value']['value'], 2)

if __name__ == '__main__':
    unittest.main()
