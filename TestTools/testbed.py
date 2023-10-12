"""Test bed tool for running tests via command line"""
import importlib.util
import os
import argparse
import json
import test_tools


def get_args():
    """Retreives arguments from the command line/terminal"""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    parser.add_argument(
        "-t", "--testfile", required=True, action="store", metavar="<test filename>"
    )
    return parser.parse_args()


def read_test_file(filename):
    """Reads test JSON data"""
    test_json = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            test_json = json.load(file)
    except FileNotFoundError:
        print(f"Error: File {filename} does not exist")
        return None
    except json.JSONDecodeError as err:
        print(f"JSON Syntax Error: {err.msg}")
        return None

    if "tests" not in test_json:
        print('Error: JSON File must have a "tests" object.')
        return None

    if not isinstance(test_json["tests"],list) or len(test_json["tests"]) <= 0:
        print('Error: No tests found')
        return None

    valid_data = True
    for num,test_data in enumerate(test_json["tests"]):
        if not isinstance(test_data,dict):
            print(f'Error in test {num + 1} "{test_data["name"]}":'
                  ' Test must be a JSON obj')
            valid_data = False
            continue
        if "function" not in test_data:
            print(f'Error in test {num + 1} "{test_data["name"]}":'
                  ' Each test must have a "function" section to run.')
            valid_data = False
            continue
        if "config" not in test_data:
            print(f'Error in test {num + 1} "{test_data["name"]}":'
                  ' Each test must have a "config" section.')
            valid_data = False
            continue

        # Convert/remove rval as needed. This is because I cannot set the
        # default value in a JSON file, so I defined a new undefined string
        # along with a prefix 'r:' that allows setting the literal string
        # 'undefined'
        rval_hold = test_data["config"].pop("expect_rval","undefined")
        if rval_hold != "undefined":
            if isinstance(rval_hold,str) and rval_hold.startswith("r:"):
                test_data["config"]["expect_rval"] = rval_hold[2:]
            else:
                test_data["config"]["expect_rval"] = rval_hold

    if not valid_data:
        return None

    return test_json


def read_program(filename):
    """Imports program file into it's own namespace"""
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist")
        return None

    mod_name = str(os.path.splitext(os.path.basename(filename))[0])

    spec = importlib.util.spec_from_file_location(mod_name, filename)
    program = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(program)

    return program


def main():
    """Entry point of the program"""
    args = get_args()

    test_json = read_test_file(args.testfile) or None
    if test_json is None:
        return

    program = read_program(args.filename) or None
    if program is None:
        return

    os.chdir(os.path.dirname(args.filename))

    passed = 0
    failed_tests = []
    total_tests = len(test_json['tests'])
    terminal_width = int(os.get_terminal_size().columns)
    file_basename = os.path.basename(args.filename)
    num_equals = int((terminal_width - len(file_basename))/2) - 1

    print(test_tools.Tcolors.fg.yellow)
    print(f"Running tests in {os.path.basename(args.testfile)} ...")

    print(f"{'='*num_equals} {file_basename} {'='*num_equals}")
    print(test_tools.Tcolors.default)

    for num,test_settings in enumerate(test_json["tests"]):
        try:
            test = test_tools.UnitTestPack(
                getattr(program, test_settings["function"]),
                *(test_settings.get("args",[])),
                **(test_settings.get("kwdargs",{})),
            ).config(**test_settings["config"])
            test()
        except KeyError as err:
            print(f"{err}")

        #pylint: disable=broad-exception-caught
        except Exception:
            pass

        if test.success:
            passed += 1
        else:
            failed_tests.append(f"Test {num + 1}: {test.name}")

    print(test_tools.Tcolors.fg.yellow)
    print(f"{'='*(int(terminal_width/2)-5)} Finished {'='*(int(terminal_width/2)-5)}")

    if passed == total_tests:
        print(test_tools.Tcolors.fg.green,end='')
    print(f"{passed}/{total_tests} Tests Passed")

    if len(failed_tests) > 0:
        print("Failed tests:")
        print(test_tools.Tcolors.fg.red,end='')
        for ftest in failed_tests:
            print(f"\t{ftest}")
    print(test_tools.Tcolors.default)


if __name__ == "__main__":
    main()
