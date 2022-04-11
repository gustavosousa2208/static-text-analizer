import os
import sys
from itertools import groupby
from colorama import Fore

import error_cases
# testing IDE

def get_files(dump=False) -> list:
    files = []
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            if os.path.isdir(name):
                for file in sorted(os.listdir(name)):
                    if file.endswith(".py"):
                        files.append(os.path.abspath(name + "\\" + file))
                break
            else:
                files.append(x)

    for file in files:
        file.replace("\\", "/")

    if dump:
        for file in files:
            with open(file, 'r') as f:
                with open(str(files.index(file)) + ".py", 'w') as f2:
                    for line in f:
                        f2.write(line)
    if not files:
        print("No files found, you need to specify in the command line")
        exit()
    return files


def analyze(*files, dump=False) -> tuple[list, list]:
    errors, exceptions = [], []
    if files == ():
        files = get_files(dump)
    for file in files:
        with open(file, 'r') as f:
            error_cases.test_for_all(f.readlines(), file, errors, exceptions)
    return errors, exceptions


if __name__ == '__main__':
    # get errors list
    err, exc = analyze()

    # separate by file
    grouped_err = [list(g) for k, g in groupby(err, lambda s: s.file)]

    # sort by line number
    for x in grouped_err:
        x.sort(key=lambda s: s.line)

    # print them!
    for x in exc:
        print(Fore.RED + "Exception:", x)
        print(Fore.WHITE, "-" * 80, end="", sep="")

    for x in grouped_err:
        print(Fore.YELLOW, *x, sep="\n")
        print(Fore.WHITE, "-" * 80, end="", sep="")
