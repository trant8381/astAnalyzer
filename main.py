import re
from sys import argv, stdout
from os import walk, path
import ast


def ast_tests(func):
    tree = ast.parse(func.strip() + "\n\treturn")
    for node in ast.walk(tree):
        if type(node) == ast.FunctionDef:
            args = {}
            for item in [x for x in ast.iter_child_nodes(node)]:
                if type(item) == ast.arguments:
                    args = item.__dict__
                    break
            defaults = args["defaults"]
            for item in range(len(defaults)):
                if type(defaults[item]) != ast.Constant:
                    return True


def analyze(file_path):
    with open(file_path, 'r') as file:
        consecutive_empty_lines = 0
        in_function = False
        c = False
        for i, line in enumerate(file, start=1):
            no_strip = line
            line = line.rstrip()
            if not(no_strip.startswith("\t")):
                in_function = False
            if len(line) == 0:
                consecutive_empty_lines += 1
                continue
            if len(line) > 79:
                stdout.write(file_path + ": ")
                print(f'Line {i}: S001 Too long')
            if line.startswith(' ') and re.search(r'^ +', line).span()[1] % 4 != 0:
                stdout.write(file_path + ": ")
                print(f'Line {i}: S002 Indentation is not a multiple of four')
            if re.search(r'^[^#]*;\s*(#.*)?$', line):
                stdout.write(file_path + ": ")
                print(f'Line {i}: S003 Unnecessary semicolon')
            if re.search(r'^[^#]*\S ?#.*$', line):
                stdout.write(file_path + ": ")
                print(f'Line {i}: S004 At least two spaces '
                      'before inline comment required')
            if re.search(r'^[^#]*#.*[Tt][Oo][Dd][Oo].*$', line):
                stdout.write(file_path + ": ")
                print(f'Line {i}: S005 TODO found')
            if consecutive_empty_lines > 2:
                stdout.write(file_path + ": ")
                print(f'Line {i}: S006 More than two blank lines '
                      'used before this line')
            if re.search(r'class {2,}', line):
                stdout.write(file_path + ": ")
                print(f"Line {i}: S007 Too many spaces after 'class'")
            elif re.search(r'^class ([^A-Z].*|[A-Z](?=[a-zA-Z]*[^A-Za-z]))$', line):
                classname = re.search(r'(?<=class )(.*)(?=\(?:?\s?)$', line)
                stdout.write(file_path + ": ")
                print(f"Line {i}: S008 Class name '{classname.group(1)}' should use CamelCase")
            if re.search(r'def {2,}', line):
                in_function = True
                stdout.write(file_path + ": ")
                print(f"Line {i}: S007 Too many spaces after 'def'")
            if re.search(r'def ([^a-z_]+)', line):
                in_function = True
                function_name = re.search(r'(?<=def )(.*)(?=:?\s?)', line)
                stdout.write(file_path + ": ")
                print(f"Line {i}: S009 Function name '{function_name.group(1)}' should use snake_case")
            if re.search(r'def .*', line):
                argument_names = re.search(r'def .*\((.*)\)', line).group(1).split(",")
                in_function = True
                for item in argument_names:
                    item = item.split("=")[0].strip() if item.find("=") != -1 else item.strip()
                    if re.search(r'[^a-z_]+', item):
                        stdout.write(file_path + ": ")
                        print(f"Line {i}: S010 Argument name '{item}' should be snake_case")
                try:
                    ast_test = ast_tests(line)
                    if ast_test:
                        stdout.write(file_path + ": ")
                        print(f"Line {i}: S012 Default argument value is mutable")
                except:
                    pass
            if re.search("\\s+.*=", no_strip) and c:
                c = False
                try:
                    var = re.search("(\\s)*(\\w+)(\\s)?=", no_strip).group(2)
                    if re.search(r'[^a-z_]+', var):
                        stdout.write(file_path + ": ")
                        print(f"Line {i}: S011 Variable '{var}' should use snake_case")
                except:
                    pass
            if not c and in_function:
                c = True
            consecutive_empty_lines = 0


arg = argv[1]

if path.isdir(arg):
    directory = walk(arg)
    filepaths = []
    for subdir in directory:
        filepaths += [subdir[0] + "\\" + i for i in subdir[2]]

    for filepath in filepaths:
        if filepath.endswith(".py") and not(filepath.endswith("tests.py")):
            analyze(filepath)
else:
    analyze(arg)