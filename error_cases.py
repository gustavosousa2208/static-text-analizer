import ast
from re import match, search, findall


class Error:
    def __init__(self, path, error_type, line, message):
        self.path = path
        self.error_type = error_type
        self.line = line
        self.message = message
        self.file = self.path.split('\\')[-1]

    def __str__(self):
        return f'{self.path}: Line {self.line}: {self.error_type} {self.message}'


def line_length(file, path, errors) -> None:
    """S001: Line is too long"""
    for x in range(len(file)):
        if len(file[x]) > 80:
            errors.append(Error(path, "S001", x + 1, "Too long"))


def indentation(file, path, errors) -> None:
    """S002: Indentation is not a multiple of four"""
    for line in range(len(file)):
        count = 0
        for col in range(len(file[line])):
            if file[line][col] == ' ':
                count += 1
            else:
                break

        if count % 4 != 0:
            errors.append(Error(path, "S002", line + 1, "Indentation is not a multiple of four"))


def semicolon(file, path, errors) -> None:
    """S003: Unnecessary semicolon"""

    def register_error(index):
        errors.append(Error(path, "S003", index + 1, "Unnecessary semicolon"))

    for line in range(len(file)):
        if ";" not in file[line]:
            continue
        if "#" in file[line]:
            file[line] = file[line].split("#")[0]
        if len(file[line]) > 0:
            if file[line].count('"') >= 2 or file[line].count("'") >= 2:
                found_match = search(r'".*?"', file[line])
                if found_match is None:
                    found_match = search(r"'.*?'", file[line])
                file[line] = file[line][0:found_match.start()] + file[line][found_match.end():]

        for x in range(len(file[line])):
            if file[line][x] == ';':
                if file[line][x - 1] == ')':
                    register_error(line)
                elif file[line][x - 1] == ']':
                    register_error(line)
                elif file[line][x - 1] == '}':
                    register_error(line)
                elif file[line][x - 1].isalpha():
                    register_error(line)


def inline_comment(file, path, errors) -> None:
    """S004: At least two spaces required before inline comments"""

    for line in range(len(file)):
        if "#" in file[line]:
            if file[line].startswith("#"):
                continue
            analysing = file[line].split("#")[0]
            if analysing.endswith("  "):
                continue
            errors.append(Error(path, "S004", line + 1, "At least two spaces required before inline comments"))


def has_todo(file, path, errors) -> None:
    """S005: TODO found"""
    for line in range(len(file)):
        if "TODO" in file[line]:
            errors.append(Error(path, "S005", line + 1, "TODO found"))


def too_many_blank_lines(file, path, errors) -> None:
    """S006 More than two blank lines used before this line"""
    for line in range(len(file)):
        if file[line - 1] == '\n':
            if file[line - 2] == '\n':
                if file[line - 3] == '\n':
                    errors.append(Error(path, "S006", line + 1, "More than two blank lines used before this line"))


def too_many_spaces(file, path, errors) -> None:
    """S007 Too many spaces after 'class'"""
    for line in range(len(file)):
        if "class" in file[line]:
            if match(r'class\s[A-z]*\b', file[line]) is None:
                errors.append(Error(path, "S007", line + 1, "Too many spaces after 'class'"))

        if "def" in file[line]:
            if match(r'\s*def\s[A-z]*\b', file[line]) is None:
                errors.append(Error(path, "S007", line + 1, "Too many spaces after 'def'"))


def class_name(file, path, errors) -> None:
    """S008 Class name '{}' should use CamelCase"""

    for line in range(len(file)):
        file[line] = file[line].split("#")[0]
        if match(r"class ", file[line]) is not None:
            if not findall(r"class\s+[A-Z]", file[line]):
                string = match('class ', file[line]).string[6:].strip("\n")
                errors.append(Error(path, "S008", line + 1, "Class name" + string + " should use CamelCase"))


def function_name(file, path, errors) -> None:
    """S009 Function name '{}' should use snake_case"""
    for line in range(len(file)):
        if match(r"\s*def", file[line]):
            if match(r'\s*def\s*[a-z_0-9]*', file[line]) is not None:
                if len(match(r'\s*def\s*[a-z_0-9]*', file[line]).group(0).strip(' ')) == 3:
                    string = match(r"\s*def(.*)\(", file[line]).group(1).strip(" ")
                    errors.append(Error(path, "S009", line + 1, "Function name " + string + " should use snake_case"))
                continue
            if match(r'\s*def\s*__[a-z]*__', file[line]) is not None:
                continue
            if match(r'\s*def\s*[a-z]+\b', file[line]) is not None:
                continue
            string = match(r"\s*def(.*)\(", file[line]).group(1).strip(" ")
            errors.append(Error(path, "S009", line + 1, "Function name " + string + " should use snake_case"))


def function_parameters(walk, path, errors) -> None:
    """S010 Argument name arg_name should be written in snake_case"""
    for x in walk:
        if isinstance(x, ast.arg):
            if match(r'[a-z]*_?[a-z]+', x.arg) is None:
                errors.append(
                    Error(path, "S010", x.lineno, "Argument name " + x.arg + " should be written in snake_case"))


def var_name(walk, path, errors) -> None:
    """S011 Variable var_name should be written in snake_case"""
    for x in walk:
        if isinstance(x, ast.Assign):
            if type(x.targets[0]) == ast.Name:
                if match(r'[a-z]*_?[a-z]+\b', x.targets[0].id) is None:
                    errors.append(
                        Error(path, "S011", x.lineno,
                              "Variable " + x.targets[0].id + " should be written in snake_case"))


def mutable_arguments(walk, path, errors) -> None:
    """The default argument value is mutable"""
    for x in walk:
        if isinstance(x, ast.arguments):
            for y in x.defaults:
                if type(y) in [ast.Dict, ast.List, ast.Tuple]:
                    errors.append(Error(path, "S012", y.lineno, "The default argument value is mutable"))


def test_for_all(file, path, errors, exceptions) -> None:
    line_length(file, path, errors)
    indentation(file, path, errors)
    semicolon(file, path, errors)
    inline_comment(file, path, errors)
    has_todo(file, path, errors)
    too_many_blank_lines(file, path, errors)
    too_many_spaces(file, path, errors)
    class_name(file, path, errors)
    function_name(file, path, errors)

    try:
        walk = ast.walk(ast.parse("".join(file)))
        function_parameters(walk, path, errors)
        var_name(walk, path, errors)
        mutable_arguments(walk, path, errors)
    except Exception as err:
        err.filename = path
        exceptions.append(err)
