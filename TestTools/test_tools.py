"""Tools for testing user I/O and timeout tests"""
# Limitations:
#  - Captured output must not exceed a reasonable length for a string!


from typing import Callable, Any, Iterable
from collections import namedtuple
import builtins
import threading
import queue
import ctypes
import sys
import traceback

class Tcolors:
    """Definitions for colors within terminal text"""

    default = "\33[0m"
    bold = "\33[1m"
    underline = "\33[4m"
    nunderline = "\33[24m"
    reverse = "\33[7m"
    forward = "\33[27m"

    class fg:  # pylint: disable = invalid-name
        """Foreground colors"""

        black = "\33[30m"
        dred = "\33[31m"
        dgreen = "\33[32m"
        dyellow = "\33[33m"
        dblue = "\33[34m"
        dmagenta = "\33[35m"
        dcyan = "\33[36m"
        dgray = "\33[90m"
        gray = "\33[37m"
        red = "\33[91m"
        green = "\33[92m"
        yellow = "\33[93m"
        blue = "\33[94m"
        magenta = "\33[95m"
        cyan = "\33[96m"
        white = "\33[97m"

    class bg:  # pylint: disable = invalid-name
        """Background colors (Work in progress)"""

        black = "\33[40m"
        dred = "\33[41m"
        dgreen = "\33[42m"
        dyellow = "\33[43m"
        dblue = "\33[44m"
        dmagenta = "\33[45m"
        dcyan = "\33[46m"
        dgray = "\33[100m"
        gray = "\33[47m"
        red = "\33[101m"
        green = "\33[102m"
        yellow = "\33[103m"
        blue = "\33[104m"
        magenta = "\33[105m"
        cyan = "\33[106m"
        white = "\33[107m"


class UnitTestError(Exception):
    """Raised by unit tests when the unit test encounters an error."""


class TestTimeoutError(UnitTestError):
    """Raised by unit tests when the unit test times out."""


class UnexpectedInputError(UnitTestError):
    """Raised by unit tests when the program asks for input that is not
    provided.
    """

# Depricated
class InputGenerator(Iterable):
    """Depricated: Provides a generator for test inputs to a program requiring user
    input"""

    def __init__(self, *args):
        self._values = list(args)
        self._counter = 0
        self._i = 0
        self.print_input = True

    def input(self, _prompt: str = ""):
        """This function replaces builtins.input and raw_input"""
        rval = None
        if self._i < len(self._values):
            rval = next(self)
        else:
            raise UnexpectedInputError(
                "Program is asking for too many inputs."
            )
        if self.print_input:
            print(f"{_prompt}{rval}")

        return rval

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i < len(self._values):
            rval = self._values[self._i]
            self._i += 1
            return rval
        raise StopIteration

    def __getitem__(self, key):
        return self._values[key]

    def __len__(self):
        return len(self._values)


class UnknownValue:
    """Dummy class to specify an untested value"""


class ExceptionThread(threading.Thread):
    """Special form of thread that terminates by raising an exception"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def get_id(self):
        """Returns id of the respective thread"""
        if hasattr(self, '_thread_id'):
            return self._thread_id
        #pylint: disable=protected-access
        for id_, thread in threading._active.items():
            if thread is self:
                return id_
    def terminate(self):
        """Terminates the thread by raising SystemExit in the thread"""
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class UnitTestPack:
    """Packs a Callable object with it's arguments so it can all be
    transported together. 
    #### The Callable and args must be picklable \
    if using timouts.
    """
    #pylint: disable = attribute-defined-outside-init
    def __init__(self, func: Callable, *args, **kwds):
        # Pack function
        self.func = func
        self.args = args
        self.kwds = kwds
        self.run = self.__call__

        # Initialize Results
        self.reset_results()

        # Set Defaults
        self.name = "Untitled"
        self.timeout = 10
        self._user_input = tuple()
        self.capture_input = True
        self.print_input = True
        self.print_out = True
        self.print_err = True
        self.expect_out = None
        self.expect_err = None
        self.expect_rval = UnknownValue()
        self.expect_success = True

    def reset_results(self):
        """Resets results and is called before each run."""
        self._stdout = ""
        self._stderr = ""
        self._rval = UnknownValue()
        self._success = False
        self._diff_str = None
        self._exception = None

    # Read only properties
    @property
    def stdout(self):
        """stdout is a read only property"""
        return self._stdout

    @property
    def stderr(self):
        """stderr is a read only property"""
        return self._stderr

    @property
    def rval(self):
        """rval is a read only property"""
        return self._rval

    @property
    def success(self):
        """Success is a read only property"""
        return self._success

    @property
    def diff_str(self):
        """diff_str is a read only property"""
        return self._diff_str

    @property
    def exception(self):
        """Exception is a read only property"""
        return self._exception

    def config(self,
               name: str = None,
               timeout: int = None,
               user_input: Iterable = None,
               print_input: bool = None,
               capture_input: bool = None,
               print_out: bool = None,
               print_err: bool = None,
               expect_out: str|list[str] = None,
               expect_err: str|list[str] = None,
               expect_rval: Any = UnknownValue(),
               expect_success: bool = None
               ):
        """Configures the attributes of the class and returns self.
        Use for inline test configurations.\n
        Please use "set_args" to change function arguments after creation.
        """
        if name is not None:
            self.name = name
        if not isinstance(expect_rval, UnknownValue):
            self.expect_rval = expect_rval
        if timeout is not None:
            self.timeout = timeout
        if user_input is not None:
            self.user_input = user_input
        if print_input is not None:
            if isinstance(user_input, InputGenerator):
                self.user_input.print_input = print_input
            self.print_input = print_input
        if capture_input is not None:
            self.capture_input = capture_input
        if expect_out is not None:
            if isinstance(expect_out, str):
                self.expect_out = expect_out
            elif isinstance(expect_out, Iterable):
                self.expect_out = '\n'.join(str(x) for x in expect_out) + '\n'
            else:
                self.expect_out = str(expect_out)
        if expect_err is not None:
            if isinstance(expect_err, str):
                self.expect_err = expect_err
            elif isinstance(expect_err, Iterable):
                self.expect_err = ''.join(str(x) + '\n' for x in expect_err)
            else:
                self.expect_err = str(expect_err)
        if print_out is not None:
            self.print_out = print_out
        if print_err is not None:
            self.print_err = print_err
        if expect_success is not None:
            self.expect_success = expect_success
        return self

    @property
    def user_input(self):
        """Get user_input tuple that replaces calls to
        input() when the function is run."""
        return self._user_input

    @user_input.setter
    def user_input(self, values: Iterable):
        """Set user input to replace calls to input() with
        when the function is run."""
        if isinstance(values,str):
            self._user_input = (values,)
        elif isinstance(values,Iterable):
            self._user_input = tuple(str(x) for x in values)
        else:
            self._user_input = (str(values),)

    def get_diff(self):
        """Get difference in output of the test function from the expected 
        output provided to the class.
        """
        success = True
        diff_str = ""
        if not isinstance(self.expect_rval, UnknownValue):
            if self.rval != self.expect_rval:
                success = False
                diff_str += "".join((
                    f"\n{Tcolors.fg.yellow}====> Return Value Diff <====\n",
                    f"Received: {Tcolors.default}",
                    repr(self.rval),
                    f"\n{Tcolors.fg.yellow}Expected: {Tcolors.default}",
                    repr(self.expect_rval)
                ))
        if self.expect_out is not None:
            if self.stdout != self.expect_out:
                success = False
                diff_str += "".join((
                    f"\n{Tcolors.fg.yellow}====> Standard Output Diff <====\n",
                    f"Expected:{Tcolors.default}\n",
                    compare_diff(self.stdout,self.expect_out)
                ))
        if self.expect_err is not None:
            if self.stderr != self.expect_err:
                success = False
                diff_str += "".join((
                    f"\n{Tcolors.fg.yellow}====> Error Output Diff <====\n",
                    f"Expected:{Tcolors.default}\n",
                    compare_diff(self.stderr,self.expect_err)
                ))
        DiffResult = namedtuple("DiffResult", ('success', 'diff_str'))
        return DiffResult(success,diff_str)

    def set_args(self, *args, **kwds):
        """Set or change the arguments passed into the function by default.
        Returns self for further inline configuration.
        """
        self.args = args
        self.kwds = kwds
        return self

    def __call__(self) -> Any:
        #pylint: disable = broad-exception-caught
        print(f"{Tcolors.fg.blue}\tRunning test: {self.name} ...{Tcolors.default}")
        self.reset_results()
        try:
            # if the timeout is not set or one of the specified debuggers is
            # debugging this code, run in main thread
            if (
                self.timeout is None
                or self.timeout <= 0

                ## This was here to allow debugger to run without timing out
                ## but VSCode's Pytest tool updated so it's always in debug mode.

                # or "pydevd" in sys.modules
                # or "pdb" in sys.modules
            ):
                self._run_in_main()
            else:
                # Otherwise, run in a timed thread
                self._run_as_task()
        except Exception as exc:
            print(f"{Tcolors.fg.red}{exc.__class__.__name__}: {exc}{Tcolors.default}")
            print()
            self._exception = exc

        if self.exception is None:
            self._success, self._diff_str = self.get_diff()

        if self.success == self.expect_success:
            self._success = True
            print(f"{Tcolors.fg.green}Success{Tcolors.default}")
        else:
            print(f"{Tcolors.fg.red}Failed{Tcolors.default}")
            if self.exception is not None:
                raise self.exception
            print(self.diff_str)
        return self.rval

    def _run_in_main(self):
        real_stdout_write = sys.stdout.write
        real_stderr_write = sys.stderr.write
        real_input = builtins.input

        # For some reason this only works if the counter is
        # a mutable object and not an integer
        class Counter:
            """Mutable counter object"""
            def __init__(self):
                self.count = 0

        counter = Counter()
        def fake_input(_prompt: str = ""):
            if counter.count >= len(self._user_input):
                raise UnexpectedInputError("Program is asking for too many inputs!")
            rval = self._user_input[counter.count]
            counter.count+= 1
            if self.print_input:
                if self.capture_input:
                    self._stdout += f"{_prompt}{rval}\n"
                else:
                    real_stdout_write(Tcolors.fg.dcyan)
                real_stdout_write(
                    f"{_prompt}"
                    f"{Tcolors.underline}{rval}"
                    f"{Tcolors.default}\n")
            return rval

        def fake_stdout_write(_s):
            """
            Copies output to the stdout string and then passes
            the output to the original write function
            """
            self._stdout += _s
            if self.print_out:
                real_stdout_write(_s)

        def fake_stderr_write(_s):
            """
            Copies error output to the stderr string and then passes
            the output to the original write function
            """
            self._stderr += _s
            if self.print_err:
                real_stderr_write(Tcolors.fg.dmagenta + _s + Tcolors.default)


        # Patch user input and output for interception
        builtins.input = fake_input
        sys.stdout.write = fake_stdout_write
        sys.stderr.write = fake_stderr_write

        try:
            # Breakpoint here to hold the debugger in a timed function
            self._rval = self.func(*self.args, **self.kwds)
        finally:
            # Put everything back, even if there's an error
            builtins.input = real_input
            sys.stdout.write = real_stdout_write
            sys.stderr.write = real_stderr_write

        return self.rval

    def _start_task(self, return_queue: queue.Queue):
        # pylint: disable = broad-exception-caught
        exception_state = None
        try:
            self._run_in_main()
        except BaseException as exc:
            # Remove the traces for background functions
            tb_stack = traceback.extract_tb(exc.__traceback__)[2:]
            exception_state = (
                exc,
                f"{exc}\n\nOriginal Traceback (most recent call last):\n"
                f"{''.join(traceback.format_list(tb_stack))}"
                f"{exc.__class__.__name__}: {exc}",
            )
        return_queue.put(exception_state)
        return_queue.put(self.rval)
        return_queue.put(self.stdout)
        return_queue.put(self.stderr)

    def _run_as_task(self):


        # pylint: disable = invalid-name
        ret_queue = queue.Queue()
        p = ExceptionThread(target=self._start_task, args=(ret_queue,))

        p.start()

        # Wait for for timeout or until process finishes
        p.join(float(self.timeout))

        terminated = False

        # If thread is still active
        if p.is_alive():
            # Terminate - may not work if process is stuck for good.
            # IDK how to force if terminate doesn't work

            p.terminate()
            terminated = True
            # Give it some more time
            p.join()

        if terminated:
            raise TestTimeoutError("Test timed out.")

        if not ret_queue.empty():
            exception = ret_queue.get()
            self._rval = ret_queue.get()
            self._stdout = ret_queue.get()
            self._stderr = ret_queue.get()
            if exception is not None:
                raise type(exception[0])(exception[1])
            return self.rval
        else:
            return None

def compare_diff(str1: str, str2: str):
    """Compare two strings and show difference on each line if not equal"""
    unprintable_chars = {
        "\t":"→",
        "\n":"↵",
        "\r":"↩",
        "\b":"← ",
        "\v":"↓",
        "\a":"🕭",
        "\x00":"␀ ",
        "\x1B":"␛ ",
    }
    # pylint: disable = invalid-name
    error_on_line = False
    out_str = ""
    no_diff = True
    i1 = 0
    i2 = 0
    len1 = len(str1)
    len2 = len(str2)
    ERROR_COLOR = Tcolors.fg.red + Tcolors.underline
    while i1 < len1 and i2 < len2:
        if str1[i1] != str2[i2] and not error_on_line:
            error_on_line = True
            out_str += ERROR_COLOR
            no_diff = False
        if error_on_line and (not str2[i2].isprintable()):
            if not str2[i2] in unprintable_chars:
                out_str += "•"
            else:
                out_str += unprintable_chars[str2[i2]]

        out_str += str2[i2]

        # Re-sync the lines
        if str1[i1] == '\n':
            while i2 < len2 and str2[i2] != '\n':
                i2 += 1
                if not str2[i2].isprintable():
                    if not str2[i2] in unprintable_chars:
                        out_str += "•"
                    else:
                        out_str += unprintable_chars[str2[i2]]
                out_str += str2[i2]
            error_on_line = False
            out_str += Tcolors.default

        elif str2[i2] == '\n':
            while i1 < len1 and str1[i1] != '\n':
                i1 += 1
            error_on_line = False
            out_str += Tcolors.default

        # Increment the indecies
        if i1 < len1:
            i1 += 1
        if i2 < len2:
            i2 += 1

    if i2 < len2:
        out_str += (
            f"{ERROR_COLOR}...[{len(str2) - i2} more chars]"
        )
        no_diff = False

    if not out_str.endswith(Tcolors.default):
        out_str += Tcolors.default
    rval = ""
    if not no_diff:
        rval = out_str

    return rval
