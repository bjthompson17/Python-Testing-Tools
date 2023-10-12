# Python-Testing-Tools
The test_tools.py file features a few classes which make up a unique tool developed for testing python scripts. It includes automated testing for individual functions, user input, stdout and stderr stream comparison, and a timeout cutoff for infinite loops. Can also be used with PyTest and UnitTest Frameworks!

## Usage
Just follow the syntax in the example programs and you'll be rolling in no time! Here is some of the syntax for the things you may need to change in the example though for your convenience:

```python
...
from <path.to.test_tools> import UnitTestPack
# Imporot test file as a module
import <program.path> as program
...
test = UnitTestPack(program.<'function_name'>, <'ordered arguments'>, ..., <'keyword arguments'> = <'values'>, ...).config(

         name = <'test name'>,                         # Default is ""
         timeout = <'test timelimit in seconds'>,      # Default is 10, use -1 for no timelimit
         user_input = <'Any iterable list/tuple of inputs'>,   # Default is an empty tuple
         print_input = <True/False>,                   # Default is True. Print user input to console.
         capture_input = <True/False>,                 # Default is True. Capture user input and prompt in std output comparison.
         print_out = <True/False>,                     # Default is True. Print stdout stream during execution.
         print_err = <True/False>,                     # Default is True. Print stderr stream during execution.
         expect_out = <'expected stdout output as a string'>,   # Default is None. If left alone, will not compare std output.
         expect_err = <'expected stderr output as a string'>,   # Default is None. If left alone, will not compare err output.
         expect_rval = <'expected return value'>,      # Default is UnknownValue(). If left alone, will not compare return value.
         expect_success = <True/False>                 # Default is True. Set to False if you expect this test to fail.
    )
...
# To execute the test, just call it like a function
test()

# To see if it succeeded, check the success variable.
if test.success:
    print("Test succeeded!")

# To change the function arguments, call set_args()
test.set_args(<'new arguments', ..., <'keyword arguments'> = <'values'>, ...)

# All configurations can be modified as class variables as well.
test.user_input = <'new list of user inputs'>
test.expect_out = <'new expected output'>
test.timeout = <'new timeout'>

# or configured by calling test.config again.
test.config(
    name = <'new name'>
    expect_success = <True/False>
)

# Running the test again will yeild different results
test()
if test.success:
    print("Updated test succeeded!")
```
Also included in this directory is a testbed program that can be run from the command line. To use it, you'll need to create a JSON file containing the test configurations for each test. Here's how to use the command in the terminal:
```
usage: python3 testbed.py [-h] [-v] -t <test filename> filename

positional arguments:
  filename

options:
  -h, --help                                     show this help message and exit
  -v, --version                                  show program's version number and exit
  -t <test filename>, --testfile <test filename> *required* Path to the JSON file containing test configurations.
```
The JSON file must be configured as follows:
```
to be continued...
```

While you can just update the test parameters for all your tests, I recommend making a new test for each testcase.

**Have Fun!**
