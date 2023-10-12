"""This is an example program for the example tests to use"""

#pylint: disable = multiple-imports, wrong-import-position
import time

# This is here to make sure unit_tests module imports right because the
# __init__.py isn't doing what I think it should be doing.
import sys, os
sys.path.append(os.path.dirname(__file__))
import test_tools as unit_tests

def empty():
    """Function with no inputs or output"""
    print("Empty function works.")

def main():
    """Program entry point."""
    for _ in range(5):
        user_in = input("> ")
        print("Testing:", user_in)

def long_function(some_input=None):
    """Function that simulates a task that takes too long"""
    for _ in range(20):
        if some_input is None:
            print("Tick")
        else:
            print(some_input)
        time.sleep(1)
    return ("string", 1, True)

def throw_error(error_text:str):
    """Function that simulates an error being thrown"""
    raise RuntimeError(error_text)


if __name__ == "__main__":
    call_pack = unit_tests.UnitTestPack(long_function, "Hi").config(
        user_input=range(1,20),
        timeout=10,
        print_input=False
    )
    try:
        call_pack()
    # pylint: disable = W0718
    except Exception:
        pass
    else:
        print("Return:", call_pack.rval)
        print("\nstdout: \n" + call_pack.stdout)
        print("\nstderr: \n" + call_pack.stderr)
