from unittest import main, TestCase
from ghsec_fib_py.fib_calcs.fib_number import recurring_fibonacci_number

class ReccurringFibNumberTest(TestCase):
    def test_zero(self):
        self.assertEqual(recurring_fibonacci_number(0), 0)
    def test_negative(self):
        with self.assertRaises(ValueError) as raised_error:
            recurring_fibonacci_number(number=-1)
        self.assertEqual("Number must be greater than or equal to 0", str(raised_error.exception))
    def test_one(self):
        self.assertEqual(recurring_fibonacci_number(1), 1)
    def test_two(self):
        self.assertEqual(recurring_fibonacci_number(2), 1)
    def test_twenty(self):
        self.assertEqual(recurring_fibonacci_number(20), 6765)


if __name__ == '__main__':
    main()