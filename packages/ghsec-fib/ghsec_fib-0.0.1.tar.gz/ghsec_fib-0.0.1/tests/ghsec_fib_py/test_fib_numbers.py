from unittest import main, TestCase
from unittest.mock import patch
from ghsec_fib_py.fib_calcs.fib_numbers import calculate_numbers

class Test(TestCase):
    @patch("ghsec_fib_py.fib_calcs.fib_numbers.recurring_fibonacci_number")
    def test_calculate_numbers(self, mock_fib_calc):
        expected_outcome = [mock_fib_calc.return_value, mock_fib_calc.return_value]
        self.assertEqual(calculate_numbers(numbers=[3,4]), expected_outcome)
        self.assertEqual(len(mock_fib_calc.call_args_list), 2)
        self.assertEqual(mock_fib_calc.call_args_list[0][1], {'number': 3})
        self.assertEqual(mock_fib_calc.call_args_list[1][1], {'number': 4})

    def test_functional(self):
        self.assertEqual(calculate_numbers(numbers=[3,4,5]), [2,3,5])

if __name__ == '__main__':
    main()