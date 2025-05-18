
import unittest
from src.mod_three_fsm import ModThreeFSM

class TestModThreeFSM(unittest.TestCase):
    def setUp(self):
        self.fsm = ModThreeFSM()
    
    def test_single_bit_numbers(self):
        self.assertEqual(self.fsm.calculate_remainder("0"), 0)
        self.assertEqual(self.fsm.calculate_remainder("1"), 1)
    
    def test_two_bit_numbers(self):
        self.assertEqual(self.fsm.calculate_remainder("10"), 2)  # 2 % 3 = 2
        self.assertEqual(self.fsm.calculate_remainder("11"), 0)   # 3 % 3 = 0
    
    def test_example_cases(self):
        self.assertEqual(self.fsm.calculate_remainder("1101"), 1)  # 13 % 3 = 1
        self.assertEqual(self.fsm.calculate_remainder("1110"), 2)   # 14 % 3 = 2
        self.assertEqual(self.fsm.calculate_remainder("1111"), 0)   # 15 % 3 = 0
        self.assertEqual(self.fsm.calculate_remainder("110"), 0)    # 6 % 3 = 0
        self.assertEqual(self.fsm.calculate_remainder("1010"), 1)   # 10 % 3 = 1
    
    def test_larger_numbers(self):
        self.assertEqual(self.fsm.calculate_remainder("101010"), 0)  # 42 % 3 = 0
        self.assertEqual(self.fsm.calculate_remainder("1111000"), 0) # 120 % 3 = 0
    
    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.fsm.calculate_remainder("102")  # Invalid binary digit
        with self.assertRaises(ValueError):
            self.fsm.calculate_remainder("abc")  # Completely invalid
    
    def test_empty_string(self):
        with self.assertRaises(ValueError):
            self.fsm.calculate_remainder("")  # Edge case - empty string

if __name__ == "__main__":
    unittest.main()