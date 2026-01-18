from typing import List, Optional, Any
from parser.ast_nodes import *


class PythonEmitter:
    """Visitor для генерации Python кода из Go AST"""
    
    def __init__(self):
        self.indent_level = 0
        self.output = []
        self.imports = set()
        self.deferred_calls = []
        self.type_declarations = {}
        
    def indent(self) -> str:
        """Возвращает текущий отступ"""
        return "    " * self.indent_level
    
    def emit(self, code: str):
        """Добавляет строку кода с учетом отступа"""
        self.output.append(self.indent() + code)
    
    def emit_line(self, code: str = ""):
        """Добавляет строку кода с новой строкой"""
        if code:
            self.emit(code)
        else:
            self.output.append("")
    
    def get_output(self) -> str:
        """Возвращает финальный Python код"""
        result = []
        
        if "threading" in self.imports:
            result.append("import threading")
        if "queue" in self.imports:
            result.append("import queue")
        if "typing" in self.imports:
            result.append("from typing import Any, Dict, List, Optional, Tuple, Union, Callable")
        if self.deferred_calls:
            result.append("import atexit")
        
        if any(isinstance(t, StructType) for t in self.type_declarations.values()):
            result.append("from dataclasses import dataclass")
            result.append("")
        
        if result:
            result.append("")
        
        result.extend(self.output)
        
        return "\n".join(result)
    
    def translate(self, ast: List[ASTNode]) -> str:
        """Главная функция трансляции"""
        for node in ast:
            node.accept(self)
        return self.get_output()
    
    
    def visit_package_declaration(self, node: PackageDeclaration):
        """Package declaration -> Python comment"""
        self.emit_line(f"# Package: {node.name}")
        self.emit_line()
    
    def visit_import_declaration(self, node: ImportDeclaration):
        """Import declaration -> Python import"""
        path = node.path.strip('"')
        if path == "fmt":
            pass
        else:
           
            import_name = path.split("/")[-1]
            self.emit_line(f"# import {import_name}  # original Go import: {path}")
    
    def visit_type_spec(self, node: TypeSpec):
        """
        Обрабатывает объявление типа: type Name Type
        
        Поддерживаемые типы:
        - type MyInt int -> алиас типа
        - type MyStruct struct {...} -> Python класс
        - type MyMap map[K]V -> typing.Dict
        - type MySlice []T -> typing.List
        """
        self.type_declarations[node.name] = node.type_node
        
        if isinstance(node.type_node, StructType):
            self._emit_struct_type(node.name, node.type_node)
        elif isinstance(node.type_node, MapType):
            self.imports.add("typing")
            key_type = self._type_to_python(node.type_node.key_type)
            value_type = self._type_to_python(node.type_node.value_type)
            self.emit_line(f"{node.name} = Dict[{key_type}, {value_type}]")
        elif isinstance(node.type_node, ArrayType):
            self.imports.add("typing")
            elem_type = self._type_to_python(node.type_node.elem_type)
            self.emit_line(f"{node.name} = List[{elem_type}]")
        elif isinstance(node.type_node, FuncType):
            self.imports.add("typing")
            param_types = [self._type_to_python(p.param_type) for p in node.type_node.params]
            return_types = [self._type_to_python(r) for r in node.type_node.returns]
            
            if len(return_types) == 0:
                return_type = "None"
            elif len(return_types) == 1:
                return_type = return_types[0]
            else:
                return_type = f"Tuple[{', '.join(return_types)}]"
            
            params_str = ", ".join(param_types) if param_types else ""
            self.emit_line(f"{node.name} = Callable[[{params_str}], {return_type}]")
        else:
            base_type = self._type_to_python(node.type_node)
            self.emit_line(f"{node.name} = {base_type}")
        
        self.emit_line()
    
    def _emit_struct_type(self, name: str, node: StructType):
        """Генерирует Python класс для Go struct"""
        self.imports.add("typing")
        
        self.emit_line("@dataclass")
        self.emit_line(f"class {name}:")
        self.indent_level += 1
        
        if node.fields:
            for field in node.fields:
                field_type = self._type_to_python(field.type_node)
                for field_name in field.names:
                    self.emit_line(f"{field_name}: {field_type}")
        else:
            self.emit_line("pass")
        
        self.indent_level -= 1
        self.emit_line()
    
    def _type_to_python(self, type_node: BaseType) -> str:
        """Конвертирует Go тип в Python типовую аннотацию"""
        if isinstance(type_node, BasicType):
            go_to_python = {
                "int": "int",
                "int8": "int",
                "int16": "int",
                "int32": "int", 
                "int64": "int",
                "uint": "int",
                "uint8": "int",
                "uint16": "int",
                "uint32": "int",
                "uint64": "int",
                "float32": "float",
                "float64": "float",
                "string": "str",
                "bool": "bool",
                "byte": "bytes",
                "rune": "str",
                "uintptr": "int",
                "error": "Exception",
            }
            return go_to_python.get(type_node.name, "Any")
        
        elif isinstance(type_node, PointerType):
            self.imports.add("typing")
            base_type = self._type_to_python(type_node.base_type)
            return f"Optional[{base_type}]"
        
        elif isinstance(type_node, ArrayType):
            self.imports.add("typing")
            elem_type = self._type_to_python(type_node.elem_type)
            return f"List[{elem_type}]"
        
        elif isinstance(type_node, MapType):
            self.imports.add("typing")
            key_type = self._type_to_python(type_node.key_type)
            value_type = self._type_to_python(type_node.value_type)
            return f"Dict[{key_type}, {value_type}]"
        
        elif isinstance(type_node, StructType):
            if type_node.name:
                return type_node.name
            else:
                self.imports.add("typing")
                return "Dict[str, Any]"
        
        elif isinstance(type_node, FuncType):
            self.imports.add("typing")
            param_types = [self._type_to_python(p.param_type) for p in type_node.params]
            return_types = [self._type_to_python(r) for r in type_node.returns]
            
            if len(return_types) == 0:
                return_type = "None"
            elif len(return_types) == 1:
                return_type = return_types[0]
            else:
                return_type = f"Tuple[{', '.join(return_types)}]"
            
            params_str = ", ".join(param_types) if param_types else ""
            return f"Callable[[{params_str}], {return_type}]"
        
        elif isinstance(type_node, InterfaceType):
            self.imports.add("typing")
            return "Any"
        
        elif isinstance(type_node, ChanType):
            self.imports.add("queue")
            elem_type = self._type_to_python(type_node.elem_type)
            return f"queue.Queue[{elem_type}]"
        
        else:
            self.imports.add("typing")
            return "Any"
    
    def visit_func_declaration(self, node: FuncDeclaration):
        """Function declaration"""
        params = []
        for param in node.params:
            for name in param.names:
                params.append(name)
        
        params_str = ", ".join(params) if params else ""
        
        if node.receiver:
            receiver_type = node.receiver.type_node  
            
            if isinstance(receiver_type, PointerType):
                receiver_type = receiver_type.base_type
            
            struct_name = ""
            if isinstance(receiver_type, BasicType):
                struct_name = receiver_type.name
            elif hasattr(receiver_type, 'name'):
                struct_name = receiver_type.name
            
            receiver_name = node.receiver.names[0] if node.receiver.names else "self"
            
            full_params = f"{receiver_name}, {params_str}" if params_str else receiver_name
            self.emit_line(f"def {node.name}({full_params}):")
        else:
            self.emit_line(f"def {node.name}({params_str}):")
        
        self.indent_level += 1
        
        if not node.body.statements:
            self.emit_line("pass")
        else:
            has_defer = any(isinstance(stmt, DeferStatement) for stmt in node.body.statements)
            
            if has_defer:
                self.emit_line("try:")
                self.indent_level += 1
                
                for stmt in node.body.statements:
                    if not isinstance(stmt, DeferStatement):
                        stmt.accept(self)
                
                self.indent_level -= 1
                self.emit_line("finally:")
                self.indent_level += 1
                
                defer_stmts = [s for s in node.body.statements if isinstance(s, DeferStatement)]
                for stmt in reversed(defer_stmts):
                    call_code = stmt.call.accept(self)
                    self.emit_line(call_code)
                
                self.indent_level -= 1
            else:
                for stmt in node.body.statements:
                    stmt.accept(self)
        
        self.indent_level -= 1
        self.emit_line()
    
    def visit_block_statement(self, node: BlockStatement):
        """Block statement"""
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_if_statement(self, node: IfStatement):
        """If statement"""
        condition = self._visit_expr(node.condition)
        self.emit_line(f"if {condition}:")
        
        self.indent_level += 1
        if node.consequence.statements:
            node.consequence.accept(self)
        else:
            self.emit_line("pass")
        self.indent_level -= 1
        
        if node.alternative:
            self.emit_line("else:")
            self.indent_level += 1
            if node.alternative.statements:
                node.alternative.accept(self)
            else:
                self.emit_line("pass")
            self.indent_level -= 1
    
    def visit_for_statement(self, node: ForStatement):
        """For statement: for init; cond; post { body }"""
        if node.init:
            node.init.accept(self)
        
        cond = self._visit_expr(node.cond) if node.cond else "True"
        self.emit_line(f"while {cond}:")
        
        self.indent_level += 1
        node.body.accept(self)
        if node.post:
            node.post.accept(self)
        self.indent_level -= 1
    
    def visit_for_range_statement(self, node: ForRangeStatement):
        """
        КОНСТРУКЦИЯ #3: for-range loop
        Go: for i, v := range items { ... }
        Python: for i, v in enumerate(items): ...
        """
        iterable = self._visit_expr(node.expr)
        
        if node.key is not None and node.value is not None:
            if node.key == "_":
                self.emit_line(f"for {node.value} in {iterable}:")
            else:
                self.emit_line(f"for {node.key}, {node.value} in enumerate({iterable}):")
        elif node.key is not None:
            self.emit_line(f"for {node.key} in range(len({iterable})):")
        else:
            self.emit_line(f"for _ in {iterable}:")
        
        self.indent_level += 1
        if node.body.statements:
            node.body.accept(self)
        else:
            self.emit_line("pass")
        self.indent_level -= 1
    
    def visit_return_statement(self, node: ReturnStatement):
        """Return statement"""
        if node.results:
            values = ", ".join(self._visit_expr(expr) for expr in node.results)
            self.emit_line(f"return {values}")
        else:
            self.emit_line("return")
    
    def visit_defer_statement(self, node: DeferStatement):
        """
        КОНСТРУКЦИЯ #1: defer statement (уникальная фича Go)
        Обрабатывается в visit_func_declaration
        """
        pass
    
    def visit_go_statement(self, node: GoStatement):
        """
        КОНСТРУКЦИЯ #2: go statement (goroutines - уникальная фича Go)
        go в Go запускает функцию в отдельной горутине (легковесный поток).
        В Python транслируется в threading.Thread
        """
        self.imports.add("threading")
        
        call_code = self._visit_expr(node.call)
        if call_code:
            if call_code.startswith("lambda:"):
                self.emit_line(f"threading.Thread(target={call_code}).start()")
            else:
                self.emit_line(f"threading.Thread(target=lambda: {call_code}).start()")
    
    def _visit_expr(self, expr: Any) -> str:
        """Обрабатывает выражение и возвращает строку"""
        if expr is None:
            return "None"
        
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            if isinstance(expr.value, str):
                value = expr.value
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith('`') and value.endswith('`'):
                    value = value[1:-1]
                return f'"{value}"'
            elif isinstance(expr.value, bool):
                return str(expr.value).lower()
            elif expr.value is None:
                return "None"
            else:
                return str(expr.value)
        elif isinstance(expr, BinaryOp):
            left = self._visit_expr(expr.left)
            right = self._visit_expr(expr.right)
            
            op = expr.operator
            if op == ":=" or op == "=":
                return f"{left} = {right}"
            elif op == "&&":
                op = "and"
            elif op == "||":
                op = "or"
            elif op == "==":
                op = "=="
            elif op == "!=":
                op = "!="
            elif op == "<":
                op = "<"
            elif op == "<=":
                op = "<="
            elif op == ">":
                op = ">"
            elif op == ">=":
                op = ">="
            elif op == "+":
                op = "+"
            elif op == "-":
                op = "-"
            elif op == "*":
                op = "*"
            elif op == "/":
                op = "/"
            
            return f"{left} {op} {right}"
        elif isinstance(expr, UnaryOp):
            operand = self._visit_expr(expr.operand)
            op = expr.operator
            if op == "!":
                op = "not"
                return f"{op} {operand}"
            elif op == "&":
                return operand
            elif op == "*":
                return operand
            elif op == "<-":
                self.imports.add("queue")
                return f"{operand}.get()"
            return f"{op}{operand}"
        elif isinstance(expr, CallExpression):
            if isinstance(expr.callee, MemberAccess):
                obj = self._visit_expr(expr.callee.object)
                member = expr.callee.member
                args = ", ".join(self._visit_expr(arg) for arg in expr.arguments)

                if obj == "fmt" and member == "Println":
                    return f"print({args})"
                elif obj == "fmt" and member == "Printf":
                    return f"print({args})"
                else:
                    return f"{obj}.{member}({args})"
            else:
                func = self._visit_expr(expr.callee)
                if func == "make":
                    arg = expr.arguments[0]
                    if isinstance(arg, ChanType):
                        elem_type = self._type_to_python(arg.element_type)
                        return f"queue.Queue()"
                    elif isinstance(arg, ArrayType) and arg.length is None:
                        # make([]T)
                        return "[]"
                    elif isinstance(arg, ArrayType):
                        # make([]T, len)
                        length_expr = expr.arguments[1] if len(expr.arguments) > 1 else arg.length
                        length = self._visit_expr(length_expr) if length_expr else "0"
                        return f"[None] * {length}"
                    else:
                        args = ", ".join(self._visit_expr(arg) for arg in expr.arguments)
                        return f"{func}({args})"
                else:
                    args = ", ".join(self._visit_expr(arg) for arg in expr.arguments)
                    return f"{func}({args})"
        elif isinstance(expr, MemberAccess):
            obj = self._visit_expr(expr.object)
            return f"{obj}.{expr.member}"
        elif isinstance(expr, ChannelOperation):
            left = self._visit_expr(expr.channel)
            right = self._visit_expr(expr.value) if expr.value else ""
            self.imports.add("queue")
            return f"{left}.put({right})"
        elif isinstance(expr, CompositeLiteral):
            return self.visit_composite_literal(expr)
        elif isinstance(expr, (ArrayType, MapType, StructType, BasicType)):
            return self._type_to_python(expr)
        elif isinstance(expr, FuncDeclaration):
            params = []
            for param in expr.params:
                for name in param.names:
                    params.append(name)
            params_str = ", ".join(params) if params else ""
            
            func_name = f"anonymous_func_{id(expr)}"
            self.emit_line(f"def {func_name}({params_str}):")
            self.indent_level += 1
            
            for stmt in expr.body.statements:
                stmt.accept(self)
            
            self.indent_level -= 1
            self.emit_line()
            return func_name
        return str(expr)
    
    def visit_var_declaration(self, node: VarDeclaration):
        """Variable declaration"""
        for i, name in enumerate(node.names):
            if i < len(node.values) and node.values[i]:
                value = self._visit_expr(node.values[i])
                self.emit_line(f"{name} = {value}")
            else:
                self.emit_line(f"{name} = None")
    
    def visit_const_declaration(self, node: ConstDeclaration):
        """Constant declaration"""
        for i, name in enumerate(node.names):
            if i < len(node.values) and node.values[i]:
                value = self._visit_expr(node.values[i])
                self.emit_line(f"{name} = {value}  # constant")
    
    def visit_expression_statement(self, node: ExprStatement):
        expr_code = self._visit_expr(node.expr)
        if expr_code:
            self.emit_line(expr_code)
    
    def visit_empty_statement(self, node: EmptyStatement):
        pass
    
    def visit_struct_type(self, node: StructType):
        """Struct type обрабатывается в visit_type_spec"""
        pass
    
    def visit_map_type(self, node: MapType):
        pass
    
    def visit_array_type(self, node: ArrayType):
        pass
    
    def visit_pointer_type(self, node: PointerType):
        pass
    
    def visit_func_type(self, node: FuncType):
        pass
    
    def visit_interface_type(self, node: InterfaceType):
        pass
    
    def visit_chan_type(self, node: ChanType):
        pass
    
    def visit_identifier(self, node: Identifier):
        return node.name
    
    def visit_literal(self, node: Literal):
        return self._visit_expr(node)
    
    def visit_binary_op(self, node: BinaryOp):
        return self._visit_expr(node)
    
    def visit_unary_op(self, node: UnaryOp):
        return self._visit_expr(node)
    
    def visit_member_access(self, node: MemberAccess):
        return self._visit_expr(node)
    
    def visit_call_expression(self, node: CallExpression):
        return self._visit_expr(node)
    
    def visit_channel_operation(self, node: ChannelOperation):
        return self._visit_expr(node)
    
    def visit_composite_literal(self, node: CompositeLiteral):
        if isinstance(node.type_expr, ArrayType) or (isinstance(node.type_expr, BasicType) and node.type_expr.name == "[]"):
            elements = [self._visit_expr(elem) for elem in node.elements]
            return f"[{', '.join(elements)}]"
        elif isinstance(node.type_expr, MapType) or (isinstance(node.type_expr, BasicType) and node.type_expr.name == "map"):
            elements = []
            for elem in node.elements:
                if isinstance(elem, KeyValueExpr):
                    key = self._visit_expr(elem.key)
                    value = self._visit_expr(elem.value)
                    elements.append(f"{key}: {value}")
            return f"{{{', '.join(elements)}}}"
        elif isinstance(node.type_expr, StructType) or isinstance(node.type_expr, BasicType) or isinstance(node.type_expr, Identifier):
            struct_name = node.type_expr.name if hasattr(node.type_expr, 'name') else "object"
            elements = []
            for elem in node.elements:
                if isinstance(elem, KeyValueExpr):
                    key = elem.key.name if isinstance(elem.key, Identifier) else str(elem.key)
                    value = self._visit_expr(elem.value)
                    elements.append(f"{key}={value}")
                else:
                    elements.append(self._visit_expr(elem))
            
            args = ", ".join(elements)
            return f"{struct_name}({args})"
        return "None"
    
    def visit_key_value_expr(self, node: KeyValueExpr):
        key = self._visit_expr(node.key)
        value = self._visit_expr(node.value)
        return f"{key}: {value}"
    
    def visit_type_assertion(self, node: TypeAssertion):
        expr = self._visit_expr(node.expr)
        return expr  
    
    def visit_slice_expression(self, node: SliceExpression):
        array = self._visit_expr(node.array)
        low = self._visit_expr(node.low) if node.low else ""
        high = self._visit_expr(node.high) if node.high else ""
        max_val = self._visit_expr(node.max_val) if node.max_val and node.slice3 else ""
        
        if node.slice3:
            return f"{array}[{low}:{high}:{max_val}]"
        else:
            return f"{array}[{low}:{high}]"
    
    def visit_type_conversion(self, node: TypeConversion):
        expr = self._visit_expr(node.expr)
        target_type = self._type_to_python(node.target_type)
        return f"{target_type}({expr})"