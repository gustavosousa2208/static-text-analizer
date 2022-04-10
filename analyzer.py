import re
import sys
import os
from io import StringIO
# added comment for testing git

errors = StringIO()


def get_files():
    files = []
    if len(sys.argv) > 1:
        for x in sys.argv[1:]:
            if os.path.isdir(x):
                for file in sorted(os.listdir(x)):
                    if file.endswith(".py"):
                        files.append(os.path.abspath(x + "\\" + file))
                break
            else:
                files.append(x)

    for x in files:
        x.replace("\\", "/")
    for x in files:
        with open(x, 'r') as f:
            with open(str(files.index(x)) + ".py", 'w') as f2:
                for line in f:
                    f2.write(line)

    return files


def indentation(line):
    count = 0
    for x in range(len(line)):
        if line[x] == ' ':
            count += 1
        else:
            break

    if count % 4 != 0:
        return True

    return False


def semicolon(line):
    if ";" not in line:
        return False
    if "#" in line:
        line = line.split("#")[0]
    if len(line) > 0:
        if line.count('"') >= 2 or line.count("'") >= 2:
            match = re.search(r'".*?"', line)
            if match is None:
                match = re.search(r"'.*?'", line)
            line = line[0:match.start()] + line[match.end():]
    for x in range(len(line)):
        if line[x] == ';':
            if line[x - 1] == ')':
                return True
            elif line[x - 1] == ']':
                return True
            elif line[x - 1] == '}':
                return True
            elif line[x - 1].isalpha():
                return True
    return False


def inline_comment(line):
    analysing = ''
    if "#" in line:
        if line.startswith("#"):
            return False
        analysing = line.split("#")[0]
        if analysing.endswith("  "):
            return False
        return True


def analyze(path):
    file = path
    with open(file, 'r') as f:
        text = f.readlines()

    blank_count = 0
    for x in range(len(text)):
        if len(text[x]) > 80:
            print(f'{path}: Line {x + 1}: S001 Too long', file=errors)

        if indentation(text[x]):
            print(f'{path}: Line {x + 1}: S002 Indentation is not a multiple of four',
                  file=errors)

        if semicolon(text[x]):
            print(f'{path}: Line {x + 1}: S003 Unnecessary semicolon', file=errors)

        if inline_comment(text[x]):
            print(
                f'{path}: Line {x + 1}: S004 At least two spaces required before inline comments',
                file=errors)

        if "#" in text[x] and "todo" in text[x].lower():
            print(f'{path}: Line {x + 1}: S005 TODO found', file=errors)

        if text[x] == "\n":
            blank_count += 1
        else:
            if blank_count > 2 and text[x] != "\n":
                print(
                    f'{path}: Line {x + 1}: S006 More than two blank lines used before this line',
                    file=errors)
            blank_count = 0


def all_files(*files):
    if files == ():
        files = get_files()
    for x in files:
        analyze(x)


if __name__ == '__main__':
    # print(indentation("print('hello');  # hello"))
    # print(semicolon("print(f'Hello, {name}');  # here is an obvious comment: this prints greeting with a name"))
    # print(semicolon("print('What\'s your name?') # reading an input"))
    all_files()
    print(errors.getvalue())
