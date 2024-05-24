import ast

class PythonToBerryConverter(ast.NodeVisitor):
    def __init__(self):
        self.berry_code = []

    def visit_ClassDef(self, node):
        self.berry_code.append(f"class {node.name}")
        self.generic_visit(node)
        self.berry_code.append("end")

    def visit_FunctionDef(self, node):
        if node.name == '__init__':
            self.berry_code.append(f"def init(")
        else:
            self.berry_code.append(f"def {node.name}(")
        
        # Add function arguments
        args = [arg.arg for arg in node.args.args if arg.arg != 'self']
        self.berry_code.append(', '.join(args) + ")")

        # Visit the function body
        self.generic_visit(node)
        self.berry_code.append("end")

    def visit_Assign(self, node):
        targets = [self.get_target(target) for target in node.targets]
        self.berry_code.append(f"{' = '.join(targets)} = ")
        self.visit(node.value)

    def get_target(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_target(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self.get_target(node.value)}[{self.get_target(node.slice.value)}]"
        else:
            raise ValueError(f"Unsupported target type: {type(node)}")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.visit(node.value)

    def visit_Call(self, node):
        func_name = self.get_func_name(node.func)
        args = [self.get_node_value(arg) for arg in node.args]
        self.berry_code.append(f"{func_name}({', '.join(args)})")

    def visit_Attribute(self, node):
        self.berry_code.append(f"{self.get_func_name(node)}")

    def visit_Name(self, node):
        self.berry_code.append(f"{node.id}")

    def visit_Constant(self, node):
        self.berry_code.append(f"{node.value}")

    def get_func_name(self, node):
        if isinstance(node, ast.Attribute):
            return f"{self.get_func_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Name):
            return node.id
        return ""

    def get_node_value(self, node):
        if isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.get_func_name(node)
        elif isinstance(node, ast.Subscript):
            return f"{self.get_node_value(node.value)}[{self.get_node_value(node.slice.value)}]"
        return ""

    def convert(self, source_code):
        tree = ast.parse(source_code)
        self.visit(tree)
        return '\n'.join(self.berry_code)

def convert_python_to_berry(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()

    converter = PythonToBerryConverter()
    berry_code = converter.convert(source_code)

    output_file_path = file_path.replace('.py', '.berry')
    with open(output_file_path, 'w') as file:
        file.write(berry_code)

    print(f"Converted code written to {output_file_path}")
