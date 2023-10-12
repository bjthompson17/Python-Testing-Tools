"""Test bed tool for running tests via command line"""
import importlib.util
import os
import argparse
import json
import test_tools


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-v", "--version", action="version", version="1.0")
    parser.add_argument(
        "-t", "--testfile", required=True, action="store", metavar="<test filename>"
    )
    parser.add_argument("-o", "--outfile", action="store")
    return parser.parse_args()


def read_test_file(filename):
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

    return test_json


def read_program(filename):
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

    for test_settings in test_json["tests"]:
        try:
            test = test_tools.UnitTestPack(
                getattr(program, test_settings["function"]),
                *test_settings["args"],
                **test_settings["kwdargs"],
            ).config(**test_settings["config"])
            test()
        except KeyError as err:
            print(f"{err}")

        #pylint: disable=broad-exception-caught
        except Exception:
            pass


if __name__ == "__main__":
    main()
