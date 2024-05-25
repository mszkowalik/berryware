import ast

class MethodMappings:
    def __init__(self):
        # Mapping Python class names to Berry class names
        self.class_name_mappings = {
            'dict': 'map',
            'list': 'list',
            'bytes': 'bytes'
        }

        # Mapping Python methods to Berry methods for specific classes
        self.class_method_mappings = {
            'list': {
                'append': 'push',
                'extend': 'concat',
                'pop': 'pop',
                'clear': 'clear',
                'insert': 'insert',
                'remove': 'remove',
                'index': 'index',
                'count': 'count',
                'sort': 'sort',
                'reverse': 'reverse',
                'copy': 'copy',
                'len': 'size',
                'tostring': 'tostring',
                'resize': 'resize',
                'find': 'find',
                'concat': 'concat',
                'item': 'item',
                'setitem': 'setitem',
            },
            'map': {
                'keys': 'keys',
                'values': 'values',
                'items': 'items',
                'get': 'item',
                'pop': 'remove',
                'clear': 'clear',
                'update': 'update',
                'setdefault': 'insert',
                'copy': 'copy',
                'len': 'size',
                'contains': 'contains',
                'find': 'find',
                'insert': 'insert',
                'tostring': 'tostring',
            },
            'bytes': {
                'tostring': 'tostring',
                'fromhex': 'fromhex',
                'resize': 'resize',
                'concat': 'concat',
                'len': 'size',
                'clear': 'clear',
                'copy': 'copy',
                'get': 'get',
                'set': 'set',
                'add': 'add',
                'asstring': 'asstring',
                'fromstring': 'fromstring',
                'getbits': 'getbits',
                'setbits': 'setbits',
                'tob64': 'tob64',
                'fromb64': 'fromb64',
                'getfloat': 'getfloat',
                'setfloat': 'setfloat',
            }
        }

    def get_berry_class_name(self, python_class_name):
        return self.class_name_mappings.get(python_class_name, python_class_name)

    def get_berry_method(self, class_name, method_name):
        return self.class_method_mappings.get(class_name, {}).get(method_name, method_name)

class PythonToBerryConverter(ast.NodeVisitor):
    def __init__(self):
        self.berry_code = []
        self.indentation = 0
        self.source_lines = []
        self.local_variables = {}  # Track local variables within methods
        self.inside_method = False  # Track if we are inside a method
        self.method_mappings = MethodMappings()  # Use the method mappings
        self.name_changes = {
            'json.loads': 'json.load',
            'float': 'real',
            'None': 'nil',
            'True': 'true',
            'False': 'false'
        }
        self.defined_functions = set()  # Track defined functions
        self.variables_in_scope = {}  # Track variables and their types in the current scope

    def set_source_code(self, source_code):
        self.source_lines = source_code.splitlines()

    def indent(self):
        return '    ' * self.indentation

    def sanitize_name(self, name):
        if name == '__init__':
            return 'init'
        return name.strip('_')

    def visit_ClassDef(self, node):
        class_name = self.sanitize_name(node.name)
        self.berry_code.append(f"{self.indent()}class {class_name}")
        self.indentation += 1
        self.generic_visit(node)
        self.indentation -= 1
        self.berry_code.append(f"{self.indent()}end")

    def visit_FunctionDef(self, node):
        method_name = self.sanitize_name(node.name)
        self.defined_functions.add(method_name)  # Track the function name
        self.berry_code.append(f"{self.indent()}def {method_name}(")
        args = [arg.arg for arg in node.args.args if arg.arg != 'self']
        self.berry_code[-1] += ', '.join(args) + ")"

        self.local_variables = {arg.arg: self.get_type_annotation(arg.annotation) for arg in node.args.args if arg.annotation}
        self.variables_in_scope.update(self.local_variables)
        self.inside_method = True
        self.indentation += 1
        self.generic_visit(node)
        self.indentation -= 1
        self.inside_method = False
        self.berry_code.append(f"{self.indent()}end")

    def handle_assignment(self, target, value, annotation=None):
        target = self.get_node_value(target)
        if self.inside_method:
            if target.startswith('self.'):
                self.berry_code.append(f"{self.indent()}{target} = {value}")
                # self.local_variables[target] = annotation or 'unknown'
                self.variables_in_scope[target] = annotation or 'unknown'
            else:
                if target not in self.local_variables:
                    self.berry_code.append(f"{self.indent()}var {target} = {value}")
                    self.local_variables[target] = annotation or 'unknown'
                    self.variables_in_scope[target] = annotation or 'unknown'
                else:
                    self.berry_code.append(f"{self.indent()}{target} = {value}")
        else:
            if target not in self.local_variables:
                self.berry_code.append(f"{self.indent()}var {target} = {value}")
                self.local_variables[target] = annotation or 'unknown'
                self.variables_in_scope[target] = annotation or 'unknown'
            else:
                self.berry_code.append(f"{self.indent()}{target} = {value}")

    def visit_AnnAssign(self, node):
        value = self.get_node_value(node.value)
        annotation = self.get_type_annotation(node.annotation)
        self.handle_assignment(node.target, value, annotation)

    def visit_Assign(self, node):
        value = self.get_node_value(node.value)
        inferred_type = self.infer_type(node.value)
        for target in node.targets:
            self.handle_assignment(target, value, inferred_type)

    def infer_type(self, node):
            if isinstance(node, ast.List):
                return 'list'
            elif isinstance(node, ast.Dict):
                return 'map'
            elif isinstance(node, ast.Bytes):
                return 'bytes'
            elif isinstance(node, ast.Call):
                func_name = self.get_func_name(node.func)
                if func_name in ['list', 'dict', 'bytes']:
                    return func_name
            return 'unknown'

    def visit_Name(self, node):
        self.berry_code.append(node.id)

    def visit_Attribute(self, node):
        value = self.get_node_value(node.value)
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            self.berry_code.append(f"{value}.{node.attr}")
        else:
            self.berry_code.append(f"{value}.{node.attr}")

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self.berry_code.append(f"'{node.value}'")
        elif node.value is None:
            self.berry_code.append('nil')
        else:
            self.berry_code.append(f"{node.value}")

    def visit_Lambda(self, node):
        args = [arg.arg for arg in node.args.args]
        body = self.get_node_value(node.body)
        return f"/->{body}"

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

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.visit(node.value)
        else:
            self.berry_code.append(f"{self.indent()}{self.get_node_value(node.value)}")

    def get_type_annotation(self, annotation):
        if annotation is None:
            return None
        elif isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            return self.get_node_value(annotation)
        return None

    def visit_Call(self, node):
        call_str = self.handle_call(node)
        self.berry_code.append(f"{self.indent()}{call_str}")

    def handle_call(self, node):
        func_name = self.get_func_name(node.func)
        object_name = self.get_full_attr_name(node.func)
        args = [self.get_node_value(arg) for arg in node.args]

        # Handle method references as callbacks
        for i, arg in enumerate(node.args):
            if self.is_function_reference(arg):
                args[i] = f"/-> {self.get_node_value(arg)}()"
        # Generalize handling for method calls based on class
        if object_name in self.variables_in_scope:
            obj_class = self.variables_in_scope[object_name]
            berry_class_name = self.method_mappings.get_berry_class_name(obj_class)
            method_name = self.method_mappings.get_berry_method(berry_class_name, func_name)
            call_str = f"{self.get_node_value(node.func.value)}.{method_name}({', '.join(args)})"
        else:
            call_str = f"{self.get_node_value(node.func)}({', '.join(args)})"
        return call_str

    def is_function_reference(self, node):
        if isinstance(node, ast.Attribute):
            return node.attr in self.defined_functions  # Check if it's a known function
        return False

    def get_object_name(self, node):
        if isinstance(node, ast.Attribute):
            value = node.value
            if isinstance(value, ast.Name):
                return self.get_node_value(value)
        return None

    def visit_If(self, node):
        if isinstance(node.test, ast.Compare) and isinstance(node.test.ops[0], ast.In):
            # Convert `in` to .contains() method call
            left = self.get_node_value(node.test.left)
            comparators = node.test.comparators[0]
            if isinstance(comparators, ast.List):
                comparators = [self.get_node_value(comp) for comp in comparators.elts]
                test = ' || '.join([f'{left} == {comp}' for comp in comparators])
            elif isinstance(comparators, (ast.Str, ast.Name)):
                test = f"({self.get_node_value(comparators)}.contains({left}))"
        else:
            test = self.get_node_value(node.test)  # Remove parenthesize argument

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

    def visit_AugAssign(self, node):
        target = self.get_node_value(node.target)
        op = self.get_operator(node.op)
        value = self.get_node_value(node.value)
        self.berry_code.append(f"{self.indent()}{target} {op}= {value}")

    def get_func_name(self, node):
        if isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return ""

    def get_full_attr_name(self, node, stop_at_last=True):
        if isinstance(node, ast.Attribute):
            # If the parent is an Attribute or Name, continue recursively
            if isinstance(node.value, (ast.Attribute, ast.Name)):
                parent_full_name = self.get_full_attr_name(node.value, stop_at_last=False)
                if stop_at_last:
                    return parent_full_name
                else:
                    return parent_full_name + '.' + node.attr
            else:
                return node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return ""

    def get_node_value(self, node, parenthesize=False):
        if isinstance(node, ast.Lambda):
            return self.visit_Lambda(node)
        elif isinstance(node, ast.FunctionDef):
            return f"/->{node.name}()"
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                value = node.value.replace('\n', '\\n') # Escape newlines
                return f"'{value}'"
            elif node.value is None:
                return 'nil'
            return str(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == 'self':
                return f"self.{node.attr}"
            return f"{self.get_node_value(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self.get_node_value(node.value)}[{self.get_subscript(node.slice)}]"
        elif isinstance(node, ast.BinOp):
            left = self.get_node_value(node.left, parenthesize=True)
            right = self.get_node_value(node.right, parenthesize=True)
            op = self.get_operator(node.op)
            result = f"{left} {op} {right}"
            return f"({result})" if parenthesize else result
        elif isinstance(node, ast.UnaryOp):
            op = self.get_operator(node.op)
            operand = self.get_node_value(node.operand)
            result = f"{op}{operand}"
            return f"({result})" if parenthesize else result
        elif isinstance(node, ast.BoolOp):
            op = ' and ' if isinstance(node.op, ast.And) else ' or '
            values = [self.get_node_value(v, parenthesize=True) for v in node.values]
            result = f"({op.join(values)})"
            return f"({result})" if parenthesize else result
        elif isinstance(node, ast.Compare):
            left = self.get_node_value(node.left)
            right = self.get_node_value(node.comparators[0])
            if isinstance(node.ops[0], ast.IsNot):
                result = f"{left} != {right}"
            else:
                result = f"{left} {self.get_operator(node.ops[0])} {right}"
            return f"({result})" if parenthesize else result
        elif isinstance(node, ast.IfExp):
            body = self.get_node_value(node.body)
            test = self.get_node_value(node.test)
            orelse = self.get_node_value(node.orelse)
            result = f"{body} if {test} else {orelse}"
            return f"({result})" if parenthesize else result
        elif isinstance(node, ast.Dict):
            return self.visit_Dict(node)
        elif isinstance(node, ast.List):
            return self.visit_List(node)
        elif isinstance(node, ast.Tuple):
            return self.visit_Tuple(node)
        elif isinstance(node, ast.Call):
            return self.handle_call(node)

        elif isinstance(node, ast.JoinedStr):
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

    def get_subscript(self, node):
        if isinstance(node, ast.Index):
            return self.get_node_value(node.value)
        elif isinstance(node, ast.Slice):
            lower = self.get_node_value(node.lower) if node.lower else ''
            upper = self.get_node_value(node.upper) if node.upper else ''
            step = self.get_node_value(node.step) if node.step else ''
            return f"{lower}:{upper}:{step}"
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
        elif isinstance(op, ast.IsNot):
            return "!="
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
