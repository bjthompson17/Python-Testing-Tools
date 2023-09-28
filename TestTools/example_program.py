"""This is an example program for the unit test template to use"""
import time

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


if __name__ == "__main__":
    main()
