
import unittest
from src.mod_three_fsm import ModThreeFSM

class TestModThreeFSM(unittest.TestCase):
    def setUp(self):
        self.fsm = ModThreeFSM()
    
    # 1. Basic Functionality Tests
    def test_single_bit_numbers(self):
        """Test all possible 1-bit inputs"""
        self.assertEqual(self.fsm.calculate_remainder("0"), 0)
        self.assertEqual(self.fsm.calculate_remainder("1"), 1)
    
    # 2. State Transition Verification
    def test_two_bit_numbers(self):
        """Verify correct state transitions"""
        # Test all 2-bit combinations
        test_cases = {
            "00": 0,  # 0 → 0 (state 0)
            "01": 1,  # 0 → 1 (state 1)
            "10": 2,  # 1 → 2 (state 2)
            "11": 0   # 2 → 0 (state 0)
        }
        for binary, expected in test_cases.items():
            with self.subTest(binary=binary):
                self.assertEqual(self.fsm.calculate_remainder(binary), expected)
    
    # 3. Comprehensive Example Cases
    def test_example_cases(self):
        """Test various length binary strings"""
        test_cases = [
            ("1101", 1),   # 13 % 3 = 1
            ("1110", 2),   # 14 % 3 = 2
            ("1111", 0),   # 15 % 3 = 0
            ("110", 0),    # 6 % 3 = 0
            ("1010", 1),   # 10 % 3 = 1
            ("100000", 2), # 32 % 3 = 2 (fixed expectation)
            ("101111", 2)   # 47 % 3 = 2
        ]
        for binary, expected in test_cases:
            with self.subTest(binary=binary):
                self.assertEqual(self.fsm.calculate_remainder(binary), expected)
    
    # 4. Boundary Conditions
    def test_large_inputs(self):
        """Test with longer binary strings"""
        self.assertEqual(self.fsm.calculate_remainder("1" + "0" * 100), 1)  # 2^100 % 3 = 1
        self.assertEqual(self.fsm.calculate_remainder("10" * 50), 1)        # Pattern test
    
    # 5. Error Handling
    def test_invalid_input(self):
        """Test non-binary input rejection"""
        invalid_inputs = [
            "102",    # Invalid digit
            "abc",    # Non-numeric
            "1.1",    # Decimal
            "0b101",  # Python binary literal
            "0x1F",   # Hex
            " "       # Whitespace
        ]
        for invalid in invalid_inputs:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    self.fsm.calculate_remainder(invalid)
    
    def test_empty_string(self):
        """Test empty input handling"""
        with self.assertRaises(ValueError):
            self.fsm.calculate_remainder("")
    
    # 6. State Persistence Verification
    def test_state_persistence(self):
        """Verify FSM resets between calls"""
        self.assertEqual(self.fsm.calculate_remainder("10"), 2)  # First call
        self.assertEqual(self.fsm.calculate_remainder("10"), 2)  # Should give same result
    
    # 7. Leading Zero Cases
    def test_leading_zeros(self):
        """Test inputs with leading zeros"""
        self.assertEqual(self.fsm.calculate_remainder("001"), 1)
        self.assertEqual(self.fsm.calculate_remainder("0000"), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)