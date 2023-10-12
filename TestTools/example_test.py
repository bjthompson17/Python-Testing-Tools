"""This is a template program for reference on how to use the Python Test Tools
as a standalone Testing system."""

# pylint: disable = wrong-import-position

from test_tools import UnitTestPack, UnknownValue

# Import test file as a module
import example_program as program

# Yes pylint, I know it's protected and undocumented. We're just testing it!
# pylint: disable = protected-access
# pylint: disable = missing-function-docstring

tests = [
    UnitTestPack(program.empty).config(
        name = "Empty Test",
        timeout = None,
        user_input = None,
        print_input = None,
        capture_input = None,
        print_out = None,
        print_err = None,
        expect_out = None,
        expect_err = None,
        expect_rval = UnknownValue(),
        expect_success=None
    ),

    UnitTestPack(program.main).config(
        name = "Example Main Test",
        user_input = (1, 2, 3, 4, 5),
        capture_input = False,
        expect_out = """\
Testing: 1
Testing: 2
Testing: 3
Testing: 4
Testing: 5
"""
    ),

    UnitTestPack(program.long_function,"Hello").config(
        name = "Timeout Test",
        timeout = 5,
        expect_out="""\
Hello
Hello
Hello
Hello
Hello
""",
        expect_success=False
    )
]

if __name__ == "__main__":
    passed_tests = 0
    for i,test in enumerate(tests):
        try:
            test()
        # Catch all Exceptions, this is a test system wrapper afterall.
        # pylint: disable = broad-exception-caught
        except Exception as err:
            pass

        if test.success:
            passed_tests += 1

    print(f"{passed_tests} / {len(tests)} test(s) passed.")
