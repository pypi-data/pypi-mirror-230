import unittest
from calculator_module.calculator import Calculator  # Importing the Calculator class from the calculator.py file

class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = Calculator()

    def test_add(self):
        result = self.calculator.add(5)
        self.assertEqual(result, 5)

    def test_subtract(self):
        result = self.calculator.subtract(2)
        self.assertEqual(result, -2)

    def test_multiply(self):
        result = self.calculator.multiply(3)
        self.assertEqual(result, 0)  # Assuming the initial memory value is 0

    def test_divide(self):
        result = self.calculator.divide(2)
        self.assertEqual(result, 0)  # Assuming the initial memory value is 0

    def test_take_root(self):
        result = self.calculator.take_root(2)
        self.assertEqual(result, 0)  # Assuming the initial memory value is 0

    def test_reset_memory(self):
        self.calculator.reset_memory()
        result = self.calculator.memory
        self.assertEqual(result, 0)

if __name__ == "__main__":
    unittest.main()
