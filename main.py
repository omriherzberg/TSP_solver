import ctypes
import os

# Find the absolute path to the compiled shared library in the current folder
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libfib.dylib')

# Load the shared library
try:
    fib_lib = ctypes.CDLL(lib_path)
except OSError:
    print(f"Error: Could not find or load the library at {lib_path}.")
    print("Please make sure you have compiled the C code first!")
    exit(1)

# Define the argument types and return type for the CFib function
# We saw in your header that the C signature is: int CFib(int n);
fib_lib.CFib.argtypes = [ctypes.c_int]
fib_lib.CFib.restype = ctypes.c_int

def calculate_fibonacci(n):
    """Wrapper function to call the C Fibonacci function."""
    return fib_lib.CFib(n)

if __name__ == "__main__":
    # Let's test it with the number 10
    number = 10
    result = calculate_fibonacci(number)
    print(f"The Fibonacci number for {number} calculated in C is: {result}")
