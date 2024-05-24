import ast

class PythonToBerryConverter(ast.NodeVisitor):
    def __init__(self):
        self.berry_code = []
        self.indentation = 0
        self.source_lines = []
        self.name_changes = {
            'json.loads': 'json.load',
            'float': 'real',
            'None': 'nil',
        }

    def set_source_code(self, source_code):
        self.source_lines = source_code.splitlines()

    def indent(self):
        return '    ' * self.indentation

    def visit_ClassDef(self, node):
        self.berry_code.append(f"{self.indent()}class {node.name}")
        self.indentation += 1
        self.generic_visit(node)
        self.indentation -= 1
        self.berry_code.append(f"{self.indent()}end")

    def visit_FunctionDef(self, node):
        if node.name == '__init__':
            self.berry_code.append(f"{self.indent()}def init(")
        else:
            self.berry_code.append(f"{self.indent()}def {node.name}(")

        # Add function arguments
        args = [arg.arg for arg in node.args.args if arg.arg != 'self']
        self.berry_code[-1] += ', '.join(args) + ")"

        self.indentation += 1
        self.generic_visit(node)
        self.indentation -= 1
        self.berry_code.append(f"{self.indent()}end")

    def visit_Try(self, node):
        self.berry_code.append(f"{self.indent()}try")
        self.indentation += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation -= 1

        for handler in node.handlers:
            if handler.type is None:
                self.berry_code.append(f"{self.indent()}except .. as {handler.name}")
            else:
                # We don't need to handle specific exception types, so we just use `..`
                self.berry_code.append(f"{self.indent()}except .. as {handler.name}")
            self.indentation += 1
            for stmt in handler.body:
                self.visit(stmt)
            self.indentation -= 1

        if node.finalbody:
            self.berry_code.append(f"{self.indent()}finally")
            self.indentation += 1
            for stmt in node.finalbody:
                self.visit(stmt)
            self.indentation -= 1

        self.berry_code.append(f"{self.indent()}end")

    def visit_Assign(self, node):
        targets = [self.get_target(target) for target in node.targets]
        value = self.get_node_value(node.value)
        if isinstance(node.value, ast.List):
            value = '[]'
        self.berry_code.append(f"{self.indent()}{' = '.join(targets)} = {value}")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.visit(node.value)
        else:
            self.berry_code.append(f"{self.indent()}{self.get_node_value(node.value)}")

    def visit_Call(self, node):
        func_name = self.get_func_name(node.func)
        args = [self.get_node_value(arg) for arg in node.args]
        self.berry_code.append(f"{self.indent()}{func_name}({', '.join(args)})")

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            # Convert `in` to .contains() method call
            left = self.get_node_value(node.test.left)
            comparators = node.test.comparators[0]
            if isinstance(comparators, ast.Str):
                test = f"({self.get_node_value(comparators)}.contains({left}))"
            else:
                test = f"({self.get_node_value(comparators)}.contains({left}))"
        else:
            test = self.get_node_value(node.test)

        self.berry_code.append(f"{self.indent()}if {test}")
        self.indentation += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation -= 1

        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self.berry_code.append(f"{self.indent()}elif {self.get_node_value(node.orelse[0].test)}")
                self.indentation += 1
                for stmt in node.orelse[0].body:
                    self.visit(stmt)
                self.indentation -= 1
                # Handle nested elif
                self.handle_elif(node.orelse[0])
            else:
                self.berry_code.append(f"{self.indent()}else")
                self.indentation += 1
                for stmt in node.orelse:
                    self.visit(stmt)
                self.indentation -= 1

        self.berry_code.append(f"{self.indent()}end")

    def handle_elif(self, node):
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self.berry_code.append(f"{self.indent()}elif {self.get_node_value(node.orelse[0].test)}")
                self.indentation += 1
                for stmt in node.orelse[0].body:
                    self.visit(stmt)
                self.indentation -= 1
                self.handle_elif(node.orelse[0])
            else:
                self.berry_code.append(f"{self.indent()}else")
                self.indentation += 1
                for stmt in node.orelse:
                    self.visit(stmt)
                self.indentation -= 1

    def visit_For(self, node):
        target = self.get_node_value(node.target)
        iter = self.get_node_value(node.iter)

        # Check if iter is a call to .keys() on a dictionary
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute) and node.iter.func.attr == 'keys':
            dict_name = self.get_node_value(node.iter.func.value)
            self.berry_code.append(f"{self.indent()}for {target} : {dict_name}.keys()")
        else:
            raise ValueError(f"Unsupported for loop iterable: {ast.dump(node.iter)}")

        self.indentation += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation -= 1
        self.berry_code.append(f"{self.indent()}end")

    def visit_While(self, node):
        test = self.get_node_value(node.test)
        self.berry_code.append(f"{self.indent()}while {test}")
        self.indentation += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation -= 1
        self.berry_code.append(f"{self.indent()}end")
        if node.orelse:
            self.berry_code.append(f"{self.indent()}else")
            self.indentation += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indentation -= 1
            self.berry_code.append(f"{self.indent()}end")

    def visit_Return(self, node):
        if node.value:
            return_value = self.get_node_value(node.value)
            self.berry_code.append(f"{self.indent()}return {return_value}")
        else:
            self.berry_code.append(f"{self.indent()}return")

    def visit_Dict(self, node):
        items = [f"{self.get_node_value(k)}: {self.get_node_value(v)}" for k, v in zip(node.keys, node.values)]
        return "{" + ", ".join(items) + "}"

    def visit_List(self, node):
        elements = [self.get_node_value(elt) for elt in node.elts]
        return "[" + ", ".join(elements) + "]"

    def visit_Tuple(self, node):
        elements = [self.get_node_value(elt) for elt in node.elts]
        return "(" + ", ".join(elements) + ")"

    def get_target(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_target(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self.get_target(node.value)}[{self.get_subscript(node.slice)}]"
        elif isinstance(node, ast.Call):
            return self.get_node_value(node)
        else:
            raise ValueError(f"Unsupported target type: {type(node)}")

    def get_subscript(self, node):
        if isinstance(node, ast.Index):
            return self.get_node_value(node.value)
        elif isinstance(node, ast.Slice):
            lower = self.get_node_value(node.lower) if node.lower else ''
            upper = self.get_node_value(node.upper) if node.upper else ''
            step = self.get_node_value(node.step) if node.step else ''
            return f"{lower}:{upper}:{step}"
        elif isinstance(node, ast.Subscript):
            return self.get_target(node)
        elif isinstance(node, ast.Constant):
            return self.get_node_value(node)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.BinOp):
            return self.get_node_value(node)
        elif isinstance(node, ast.UnaryOp):
            return self.get_node_value(node)
        else:
            raise ValueError(f"Unsupported subscript type: {type(node)}")

    def visit_AugAssign(self, node):
        target = self.get_node_value(node.target)
        op = self.get_operator(node.op)
        value = self.get_node_value(node.value)
        self.berry_code.append(f"{self.indent()}{target} {op}= {value}")

    def visit_Attribute(self, node):
        self.berry_code.append(f"{self.get_func_name(node)}")

    def visit_Name(self, node):
        self.berry_code.append(f"{node.id}")

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self.berry_code.append(f"'{node.value}'")
        else:
            self.berry_code.append(f"{node.value}")

    def get_func_name(self, node):
        if isinstance(node, ast.Attribute):
            return f"{self.get_func_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Name):
            return node.id
        return ""

    def get_node_value(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f"'{node.value}'"
            return str(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self.get_func_name(node)
        elif isinstance(node, ast.Subscript):
            return f"{self.get_node_value(node.value)}[{self.get_subscript(node.slice)}]"
        elif isinstance(node, ast.BinOp):
            left = self.get_node_value(node.left)
            right = self.get_node_value(node.right)
            op = self.get_operator(node.op)
            return f"{left} {op} {right}"
        elif isinstance(node, ast.UnaryOp):
            op = self.get_operator(node.op)
            operand = self.get_node_value(node.operand)
            if op == "not ":
                return f"{op}({operand})"
            return f"{op}{operand}"
        elif isinstance(node, ast.BoolOp):
            op = ' and ' if isinstance(node.op, ast.And) else ' or '
            values = [self.get_node_value(v) for v in node.values]
            return f"({op.join(values)})"
        elif isinstance(node, ast.Compare):
            left = self.get_node_value(node.left)
            ops = [self.get_operator(op) for op in node.ops]
            comparators = [self.get_node_value(comp) for comp in node.comparators]
            if isinstance(node.ops[0], ast.IsNot):
                return f"{left} != {' '.join(comparators)}"
            if isinstance(node.ops[0], ast.In):
                comparator = node.comparators[0]
                if isinstance(comparator, ast.List):
                    comparators = [self.get_node_value(comp) for comp in comparator.elts]
                    return f"({left} == {' || '.join(comparators)})"
                elif isinstance(comparator, (ast.Name, ast.Attribute)):
                    return f"{self.get_node_value(comparator)}.contains({left})"
            return f"{left} {' '.join(ops)} {' '.join(comparators)}"
        elif isinstance(node, ast.IfExp):
            body = self.get_node_value(node.body)
            test = self.get_node_value(node.test)
            orelse = self.get_node_value(node.orelse)
            return f"{body} if {test} else {orelse}"
        elif isinstance(node, ast.Dict):
            return self.visit_Dict(node)
        elif isinstance(node, ast.List):
            return self.visit_List(node)
        elif isinstance(node, ast.Tuple):
            return self.visit_Tuple(node)
        elif isinstance(node, ast.Call):
            func_name = self.get_func_name(node.func)
            args = [self.get_node_value(arg) for arg in node.args]
            if func_name == "str.format":
                # Handle string formatting
                format_string = args[0]
                format_args = ", ".join(args[1:])
                return f"string.format({format_string}, {format_args})"
            return f"{func_name}({', '.join(args)})"
        elif isinstance(node, ast.JoinedStr):
            # Convert f-string to string.format
            format_string_parts = []
            format_values = []
            for value in node.values:
                if isinstance(value, ast.Str):
                    format_string_parts.append(value.s)
                elif isinstance(value, ast.FormattedValue):
                    format_string_parts.append('%s')
                    format_values.append(self.get_node_value(value.value))
            format_string = ''.join(format_string_parts)
            return f"string.format('{format_string}', {', '.join(format_values)})"
        return ""


    def get_operator(self, op):
        if isinstance(op, ast.Add):
            return "+"
        elif isinstance(op, ast.Sub):
            return "-"
        elif isinstance(op, ast.Mult):
            return "*"
        elif isinstance(op, ast.Div):
            return "/"
        elif isinstance(op, ast.Mod):
            return "%"
        elif isinstance(op, ast.Pow):
            return "**"
        elif isinstance(op, ast.LShift):
            return "<<"
        elif isinstance(op, ast.RShift):
            return ">>"
        elif isinstance(op, ast.NotEq):
            return "!="
        elif isinstance(op, ast.Eq):
            return "=="
        elif isinstance(op, ast.Lt):
            return "<"
        elif isinstance(op, ast.LtE):
            return "<="
        elif isinstance(op, ast.Gt):
            return ">"
        elif isinstance(op, ast.GtE):
            return ">="
        elif isinstance(op, ast.AugAssign):  # Add support for augmented assignment
            if isinstance(op.op, ast.Add):
                return "+="
            elif isinstance(op.op, ast.Sub):
                return "-="
            elif isinstance(op.op, ast.Mult):
                return "*="
            elif isinstance(op.op, ast.Div):
                return "/="
        elif isinstance(op, ast.And):
            return "and"
        elif isinstance(op, ast.Or):
            return "or"
        elif isinstance(op, ast.Not):
            return "not"
        elif isinstance(op, ast.BitOr):
            return "|"
        elif isinstance(op, ast.BitXor):
            return "^"
        elif isinstance(op, ast.BitAnd):
            return "&"
        elif isinstance(op, ast.FloorDiv):
            return "//"
        elif isinstance(op, ast.Not):
            return "not "
        else:
            return ""

    def convert(self, source_code):
        # Store the source code lines for error context
        self.set_source_code(source_code)

        # Apply name changes
        for old_name, new_name in self.name_changes.items():
            source_code = source_code.replace(old_name, new_name)

        tree = ast.parse(source_code)
        self.visit(tree)
        return '\n'.join(self.berry_code)

def convert_python_to_berry(input_file_path):
    with open(input_file_path, 'r') as file:
        source_code = file.read()

    converter = PythonToBerryConverter()
    berry_code = converter.convert(source_code)

    output_file_path = input_file_path.replace('.py', '.be')
    with open(output_file_path, 'w') as file:
        file.write(berry_code)

    print(f"Converted code written to {output_file_path}")
