import ast
from typing import Dict, List, Any
import pandas as pd


def extract_code_info_from_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as f:
        code = f.read()
    return extract_code_info(code)


def extract_code_info_from_files(file_paths: List[str]) -> Dict[str, Any]:
    code_info = {
        "Functions": [],
        "Classes": [],
        "Imports": [],
        "Libraries": [],
        "Patterns": [],
    }
    for file_path in file_paths:
        file_code_info = extract_code_info_from_file(file_path)
        if file_code_info:
            for key in code_info.keys():
                code_info[key].extend(file_code_info[key])
    return code_info


def create_code_info_df(code_info: Dict[str, Any]) -> pd.DataFrame:
    code_info_df = pd.DataFrame(
        [code_info]
    )  # Creates a DataFrame with one row and multiple columns

    # Safely convert string-represented Python literals to actual Python objects
    for column in ["Imports", "Libraries", "Functions", "Classes", "Patterns"]:
        if column in code_info_df.columns:
            code_info_df[column] = code_info_df[column].apply(
                lambda x: ast.literal_eval(str(x)) if x else []
            )

    return code_info_df


def create_code_info_df_from_files(file_paths: List[str]) -> pd.DataFrame:
    code_info = extract_code_info_from_files(file_paths)
    return create_code_info_df(code_info)


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.function_info = []
        self.class_info = []
        self.import_info = []
        self.control_flow_info = []
        self.used_imports = set()
        self.external_libraries = set()
        self.pattern_info = []

    def visit_Import(self, node):
        for n in node.names:
            self.import_info.append(
                {
                    "type": "import",
                    "module": n.name,
                    "name": n.asname if n.asname else n.name,
                }
            )
            self.external_libraries.add(n.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for n in node.names:
            self.import_info.append(
                {
                    "type": "from",
                    "module": node.module,
                    "name": n.name,
                    "asname": n.asname if n.asname else n.name,
                }
            )
            self.external_libraries.add(node.module.split(".")[0])
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        docstring = ast.get_docstring(node, clean=True)  # Extracting docstring
        self.class_info.append(
            {
                "name": node.name,
                "methods": [],
                "control_flow": [],
                "docstring": docstring,
            }
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        docstring = ast.get_docstring(node, clean=True)  # Extracting docstring
        variables = {}
        control_flow = []
        if self.class_info:
            class_methods = self.class_info[-1]["methods"]
            params = [param.arg for param in node.args.args]
            class_methods.append(
                {
                    "name": node.name,
                    "parameters": params,
                    "return_value": None,
                    "variables": variables,
                    "control_flow": control_flow,
                    "docstring": docstring,  # Adding docstring
                }
            )
        else:
            params = [param.arg for param in node.args.args]
            self.function_info.append(
                {
                    "name": node.name,
                    "parameters": params,
                    "return_value": None,
                    "variables": variables,
                    "control_flow": control_flow,
                    "docstring": docstring,  # Adding docstring
                }
            )
        self.control_flow_info = control_flow
        self.generic_visit(node)

    def visit_Return(self, node):
        if self.class_info:
            class_methods = self.class_info[-1]["methods"]
            if class_methods:
                class_methods[-1]["return_value"] = ast.dump(node.value)
        elif self.function_info:
            self.function_info[-1]["return_value"] = ast.dump(node.value)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if self.class_info:
            class_methods = self.class_info[-1]["methods"]
            if class_methods:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        class_methods[-1]["variables"][target.id] = ast.dump(node.value)
        elif self.function_info:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.function_info[-1]["variables"][target.id] = ast.dump(
                        node.value
                    )
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.pattern_info.append(
            {
                "type": "List Comprehension",
                "expression": ast.dump(node.elt),
                "loops": [ast.dump(loop) for loop in node.generators],
            }
        )
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self.pattern_info.append(
            {
                "type": "Generator Expression",
                "expression": ast.dump(node.elt),
                "loops": [ast.dump(loop) for loop in node.generators],
            }
        )
        self.generic_visit(node)

    def visit_Lambda(self, node):
        self.pattern_info.append(
            {
                "type": "Lambda Function",
                "expression": ast.dump(node.body),
                "args": [arg.arg for arg in node.args.args],
            }
        )
        self.generic_visit(node)

    def visit_For(self, node):
        self.control_flow_info.append(
            {
                "type": "for",
                "target": ast.dump(node.target),
                "iter": ast.dump(node.iter),
            }
        )
        self.generic_visit(node)

    def visit_While(self, node):
        self.control_flow_info.append({"type": "while", "test": ast.dump(node.test)})
        self.generic_visit(node)

    def visit_If(self, node):
        self.control_flow_info.append({"type": "if", "test": ast.dump(node.test)})
        self.generic_visit(node)

    def visit_Try(self, node):
        exception_info = []
        for handler in node.handlers:
            exception_type = ast.dump(handler.type) if handler.type else None
            exception_name = handler.name if handler.name else None
            exception_info.append({"type": exception_type, "name": exception_name})

        self.control_flow_info.append({"type": "try", "exceptions": exception_info})

        self.generic_visit(node)


def extract_code_info(code: str) -> Dict[str, Any]:
    analyzer = CodeAnalyzer()
    try:
        analyzer.visit(ast.parse(code))
        code_info = {
            "Functions": [],
            "Classes": [],
            "Imports": [],
            "Libraries": [],
            "Patterns": [],
        }

        # Extract function information
        for func in analyzer.function_info:
            code_info["Functions"].append(func)

        # Extract class information
        for cls in analyzer.class_info:
            code_info["Classes"].append(cls)

        # Extract import information
        for imp in analyzer.import_info:
            code_info["Imports"].append(imp)

        # Extract pattern information
        for pattern in analyzer.pattern_info:
            code_info["Patterns"].append(pattern)

        # Check which imported external libraries are actually used
        for lib in analyzer.external_libraries:
            if lib in analyzer.used_imports:
                code_info["Libraries"].append(lib)
        return code_info

    except SyntaxError as e:
        invalid_line = e.lineno - 1
        code_lines = code.split("\n")
        del code_lines[invalid_line]
        # Remove whitespace lines
        code_lines = [line for line in code_lines if line.strip()]
        code = "\n".join(code_lines)

        if len(code_lines) == 0:
            return False, "No valid code left."
        elif len(code_lines) == 1:
            return False, "Syntax error in the remaining code."
        # Continue the loop to attempt parsing again
        return extract_code_info(code)
