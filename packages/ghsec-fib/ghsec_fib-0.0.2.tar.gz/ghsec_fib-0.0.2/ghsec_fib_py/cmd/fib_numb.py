import argparse
from ghsec_fib_py.fib_calcs.fib_number import recurring_fibonacci_number

def fib_numb() -> None:
    parser = argparse.ArgumentParser(description='Calculate the recurring Fibonacci number for a given number.')
    parser.add_argument('--number', action='store', type=int, required=True, help='The number to calculate the recurring Fibonacci number for.')
    args = parser.parse_args()
    print(f"Your Fibonacci number is: {recurring_fibonacci_number(args.number)}")