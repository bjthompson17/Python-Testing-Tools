# Python-Testing-Tools
The test_tools.py file features a few classes which make up a unique tool developed for testing python scripts. It includes automated testing for individual functions, user input, stdout and stderr stream comparison, and a timeout cutoff for infinite loops. Can also be used with PyTest and UnitTest Frameworks!

## Usage
Just follow the syntax in the example programs and you'll be rolling in no time! Here is some of the syntax for the things you may need to change in the example though for your convenience:

### Test_tools.py
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

While you can just update the test parameters for all your tests, I recommend making a new test for each testcase.

### Testbed.py

The testbed.py file has been added as a command line tool for those that wish to run their tests from the command prompt rather than write a python file for every test. To use testbed.py, you'll first need to create a JSON file containing the test configurations for each test. After that, you may execute the test by passing in the JSON test file and your Python script to test. The following is the command line help page for testbed.py:
```
usage: python3 testbed.py [-h] [-v] -t <test filename> filename

positional arguments:
  filename

options:
  -h, --help                                     show this help message and exit
  -v, --version                                  show program's version number and exit
  -t <test filename>, --testfile <test filename> path to your JSON test file.
```

The JSON file has a specific configuration format. The following setup is the minimum requrement for this JSON file:

Note: "config" contains the same key and value information as the `.config()` function above.

```json
{
    "tests":[
        {
            "function":"<name of function to run>",
            "config":{}
        },
    ]
}
```

The above runs a test without sending any input and function arguments or expecting any output. It would only fail if an error is thrown. 

The following JSON configuration file does *exactly the same thing*, but it has every possible element defined with it's default value:

Note: `null` is used instead of `None` and "undefined" is used instead of UnknownValue. If you need to expect literal string "undefined" for the return value, use "r:undefined" instead. Anything past "r:" is interpreted literally.

```json
{
    "tests":[
        {
            "function":"<name of function to run>",
            "args":[],
            "kwargs":{},
            "config":{
                "name": null,
                "timeout": null,
                "user_input":null,
                "print_input": null,
                "capture_input": null,
                "print_out": null,
                "print_err": null,
                "expect_out": null,
                "expect_err": null,
                "expect_rval": "undefined",
                "expect_success": null
            }
        }
    ]
}
```
There is one more catch to `expect_out` and `expect_err`, since you can't have multi-line strings in JSON, I've included to capablitity for it to concatenate lists of strings. To include multiple lines of output for `expect_out`, do one of the following:

```json
{
    "tests":[
        {
            "function":"main",
            "config":{
                "name":"Multi-line with lists",
                "expect_out":[
                    "Line 1",
                    "Line 2",
                    "Line 3"
                ]
            }
        },
        {
            "function":"main",
            "config":{
                "name":"Multi-line with newline",
                "expect_out":"Line 1\nLine 2\nLine 3\n"
            }
        }
    ]
}
```

**Have Fun!**
