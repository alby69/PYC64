import unittest
from pyc64c.engine import run_pipeline

class TestAdvancedTypes(unittest.TestCase):
    def test_multidimensional_array(self):
        # Declare 2D array, assign value, retrieve and print it
        src = """
arr: byte[3][4]
def main():
    arr[1, 2] = 42
    x: byte = arr[1, 2]
    print(x)
"""
        res = run_pipeline(src, {"simulate": True})
        self.assertTrue(res.success)
        # Check that simulation actually executed and outputted '42'
        self.assertIn("42", res.simulation_output)

    def test_struct_declaration_and_field_access(self):
        # Declare struct type, struct variable, assign and add fields
        src = """
struct Point:
    x: byte
    y: byte

p: Point
def main():
    p.x = 10
    p.y = 20
    val: byte = p.x + p.y
    print(val)
"""
        res = run_pipeline(src, {"simulate": True})
        self.assertTrue(res.success)
        # Check that struct fields were accessed, offset calculated, and result printed is '30'
        self.assertIn("30", res.simulation_output)

    def test_pointer_operations(self):
        # Declare variable, pointer, assign address, dereference to write and read
        src = """
val: byte = 100
p_val: ptr
def main():
    p_val = &val
    *p_val = 200
    res: byte = *p_val
    print(res)
"""
        res = run_pipeline(src, {"simulate": True})
        self.assertTrue(res.success)
        # Check that pointer operations modified the value and printed '200'
        self.assertIn("200", res.simulation_output)

    def test_high_level_dsl(self):
        # High level DSL with virtual MethodCall compilation to built-ins
        src = """
struct Sprite:
    id: byte

s: Sprite

def main():
    s.id = 1
    s.color(5)
"""
        res = run_pipeline(src, {"simulate": True})
        self.assertTrue(res.success)

if __name__ == '__main__':
    unittest.main()
