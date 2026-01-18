from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union, Dict

class ASTNode(ABC):
    """Базовый класс для всех узлов AST"""
    @abstractmethod
    def accept(self, visitor: 'Visitor') -> Any:
        """Паттерн Посетитель для обхода AST"""
        pass

class Visitor(ABC):
    """Базовый класс для посетителей AST"""
    @abstractmethod
    def visit_identifier(self, node: 'Identifier') -> Any: pass
    @abstractmethod
    def visit_literal(self, node: 'Literal') -> Any: pass
    @abstractmethod
    def visit_binary_op(self, node: 'BinaryOp') -> Any: pass
    @abstractmethod
    def visit_unary_op(self, node: 'UnaryOp') -> Any: pass
    @abstractmethod
    def visit_call_expression(self, node: 'CallExpression') -> Any: pass
    @abstractmethod
    def visit_block_statement(self, node: 'BlockStatement') -> Any: pass
    @abstractmethod
    def visit_var_declaration(self, node: 'VarDeclaration') -> Any: pass
    @abstractmethod
    def visit_func_declaration(self, node: 'FuncDeclaration') -> Any: pass
    @abstractmethod
    def visit_parameter(self, node: 'Parameter') -> Any: pass
    @abstractmethod
    def visit_struct_type(self, node: 'StructType') -> Any: pass
    @abstractmethod
    def visit_field(self, node: 'Field') -> Any: pass
    @abstractmethod
    def visit_if_statement(self, node: 'IfStatement') -> Any: pass
    @abstractmethod
    def visit_for_range_statement(self, node: 'ForRangeStatement') -> Any: pass
    @abstractmethod
    def visit_return_statement(self, node: 'ReturnStatement') -> Any: pass
    @abstractmethod
    def visit_defer_statement(self, node: 'DeferStatement') -> Any: pass
    @abstractmethod
    def visit_go_statement(self, node: 'GoStatement') -> Any: pass
    @abstractmethod
    def visit_channel_operation(self, node: 'ChannelOperation') -> Any: pass
    @abstractmethod
    def visit_package_declaration(self, node: 'PackageDeclaration') -> Any: pass
    @abstractmethod
    def visit_import_declaration(self, node: 'ImportDeclaration') -> Any: pass
    @abstractmethod
    def visit_member_access(self, node: 'MemberAccess') -> Any: pass
    @abstractmethod
    def visit_composite_literal(self, node: 'CompositeLiteral') -> Any: pass
    @abstractmethod
    def visit_type_spec(self, node: 'TypeSpec') -> Any: pass
    @abstractmethod
    def visit_interface_type(self, node: 'InterfaceType') -> Any: pass
    @abstractmethod
    def visit_method_spec(self, node: 'MethodSpec') -> Any: pass
    @abstractmethod
    def visit_select_statement(self, node: 'SelectStatement') -> Any: pass
    @abstractmethod
    def visit_case_clause(self, node: 'CaseClause') -> Any: pass
    @abstractmethod
    def visit_switch_statement(self, node: 'SwitchStatement') -> Any: pass
    @abstractmethod
    def visit_type_switch_statement(self, node: 'TypeSwitchStatement') -> Any: pass
    @abstractmethod
    def visit_type_assertion(self, node: 'TypeAssertion') -> Any: pass
    @abstractmethod
    def visit_slice_expression(self, node: 'SliceExpression') -> Any: pass
    @abstractmethod
    def visit_pointer_type(self, node: 'PointerType') -> Any: pass
    @abstractmethod
    def visit_map_type(self, node: 'MapType') -> Any: pass
    @abstractmethod
    def visit_array_type(self, node: 'ArrayType') -> Any: pass
    @abstractmethod
    def visit_func_type(self, node: 'FuncType') -> Any: pass
    @abstractmethod
    def visit_label_statement(self, node: 'LabelStatement') -> Any: pass
    @abstractmethod
    def visit_goto_statement(self, node: 'GotoStatement') -> Any: pass
    @abstractmethod
    def visit_break_statement(self, node: 'BreakStatement') -> Any: pass
    @abstractmethod
    def visit_continue_statement(self, node: 'ContinueStatement') -> Any: pass
    @abstractmethod
    def visit_type_conversion(self, node: 'TypeConversion') -> Any: pass
    @abstractmethod
    def visit_for_statement(self, node: 'ForStatement') -> Any: pass
    @abstractmethod
    def visit_assign_statement(self, node: 'AssignStatement') -> Any: pass

class Identifier(ASTNode):
    """Идентификатор: имена переменных, функций, типов и т.д."""
    def __init__(self, name: str, line: int, col: int):
        self.name = name
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_identifier(self)

class Literal(ASTNode):
    """Литеральное значение: число, строка, bool, nil"""
    def __init__(self, value: Any, line: int, col: int):
        self.value = value
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_literal(self)

class BaseType(ASTNode):
    """Базовый класс для всех типов"""
    pass

class BasicType(BaseType):
    """Базовые типы Go: int, string, bool и т.д."""
    def __init__(self, name: str, line: int, col: int):
        self.name = name
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):

        return visitor.visit_identifier(Identifier(self.name, self.line, self.col))

class PointerType(BaseType):
    """Указательный тип: *T"""
    def __init__(self, base_type: BaseType, line: int, col: int):
        self.base_type = base_type
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_pointer_type(self)

class ArrayType(BaseType):
    """Массив: [N]T"""
    def __init__(self, length: Optional[ASTNode], element_type: BaseType, line: int, col: int):
        self.length = length  
        self.element_type = element_type
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_array_type(self)

class SliceType(BaseType):
    """Слайс: []T (частный случай ArrayType с length=None)"""
    pass  

class MapType(BaseType):
    """Тип карты: map[K]V"""
    def __init__(self, key_type: BaseType, value_type: BaseType, line: int, col: int):
        self.key_type = key_type
        self.value_type = value_type
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_map_type(self)

class StructType(BaseType):
    """Структура: struct { fields }"""
    def __init__(self, name: Optional[str], fields: List['Field'], line: int, col: int):
        self.name = name  
        self.fields = fields
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_struct_type(self)

class InterfaceType(BaseType):
    """Интерфейс: interface { methods }"""
    def __init__(self, name: Optional[str], methods: List['MethodSpec'], line: int, col: int):
        self.name = name
        self.methods = methods
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_interface_type(self)

class FuncType(BaseType):
    """Тип функции: func(params) returns"""
    def __init__(self, params: List['Parameter'], returns: List[BaseType], line: int, col: int):
        self.params = params
        self.returns = returns
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_func_type(self)

class ChanType(BaseType):
    """Тип канала: chan T, <-chan T, chan<- T"""
    def __init__(self, direction: str, element_type: BaseType, line: int, col: int):
        self.direction = direction  
        self.element_type = element_type
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_identifier(Identifier(f"chan {self.element_type}", self.line, self.col))

class Field(ASTNode):
    """Поле структуры или параметр функции"""
    def __init__(self, names: List[str], type_node: BaseType, tag: Optional[str] = None, line: int = -1, col: int = -1):
        self.names = names  
        self.type_node = type_node
        self.tag = tag
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_field(self)

class Parameter(ASTNode):
    """Параметр функции или метода"""
    def __init__(self, names: List[str], type_node: BaseType, line: int, col: int):
        self.names = names
        self.type_node = type_node
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_parameter(self)

class MethodSpec(ASTNode):
    """Спецификация метода в интерфейсе"""
    def __init__(self, name: str, params: List[Parameter], returns: List[BaseType], line: int, col: int):
        self.name = name
        self.params = params
        self.returns = returns
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_method_spec(self)

class BinaryOp(ASTNode):
    """Бинарная операция: a + b, x == y и т.д."""
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int, col: int):
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_op(self)

class UnaryOp(ASTNode):
    """Унарная операция: -x, !y, &z, <-ch"""
    def __init__(self, operator: str, operand: ASTNode, line: int, col: int):
        self.operator = operator
        self.operand = operand
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_unary_op(self)

class CallExpression(ASTNode):
    """Вызов функции: fn(arg1, arg2)"""
    def __init__(self, callee: ASTNode, arguments: List[ASTNode], line: int, col: int):
        self.callee = callee
        self.arguments = arguments
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_call_expression(self)

class MemberAccess(ASTNode):
    """Доступ к члену: obj.field или pkg.Func"""
    def __init__(self, object: ASTNode, member: str, line: int, col: int):
        self.object = object
        self.member = member
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_member_access(self)

class CompositeLiteral(ASTNode):
    """Составной литерал: T{fields}"""
    def __init__(self, type_expr: BaseType, elements: List[Union[ASTNode, 'KeyValueExpr']], line: int, col: int):
        self.type_expr = type_expr
        self.elements = elements  
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_composite_literal(self)

class KeyValueExpr(ASTNode):
    """Пара ключ-значение в составных литералах: key: value"""
    def __init__(self, key: ASTNode, value: ASTNode, line: int, col: int):
        self.key = key
        self.value = value
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_op(BinaryOp(self.key, ":", self.value, self.line, self.col))

class TypeAssertion(ASTNode):
    """Утверждение типа: x.(T)"""
    def __init__(self, expr: ASTNode, asserted_type: BaseType, line: int, col: int):
        self.expr = expr
        self.asserted_type = asserted_type
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_type_assertion(self)

class SliceExpression(ASTNode):
    """Выражение среза: arr[low:high:max]"""
    def __init__(self, array: ASTNode, low: Optional[ASTNode], high: Optional[ASTNode], 
                 max: Optional[ASTNode], slice3: bool, line: int, col: int):
        self.array = array
        self.low = low
        self.high = high
        self.max = max 
        self.slice3 = slice3 
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_slice_expression(self)

class TypeConversion(ASTNode):
    """Преобразование типа: T(x)"""
    def __init__(self, type_node: BaseType, expr: ASTNode, line: int, col: int):
        self.type_node = type_node
        self.expr = expr
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_type_conversion(self)

class ChannelOperation(ASTNode):
    """Операция с каналом: ch <- val или <-ch"""
    def __init__(self, channel: ASTNode, value: Optional[ASTNode], line: int, col: int):
        self.channel = channel
        self.value = value  
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_channel_operation(self)

class Statement(ASTNode):
    """Базовый класс для всех операторов"""
    pass

class BlockStatement(Statement):
    """Блок операторов: { ... }"""
    def __init__(self, statements: List[Statement], line: int = -1, col: int = -1):
        self.statements = statements
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_block_statement(self)

class ExprStatement(Statement):
    """Выражение как оператор: fn(), x = y"""
    def __init__(self, expr: ASTNode, line: int, col: int):
        self.expr = expr
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_expression_statement(self)

class VarDeclaration(Statement):
    """Объявление переменной: var x T = val или x := val"""
    def __init__(self, names: List[str], types: List[BaseType], values: List[ASTNode], 
                 is_short: bool, line: int, col: int):
        self.names = names
        self.types = types 
        self.values = values
        self.is_short = is_short 
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_var_declaration(self)

class ConstDeclaration(Statement):
    """Объявление константы: const x = 42"""
    def __init__(self, names: List[str], types: List[BaseType], values: List[ASTNode], line: int, col: int):
        self.names = names
        self.types = types
        self.values = values
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_var_declaration(VarDeclaration(
            self.names, self.types, self.values, False, self.line, self.col))

class TypeSpec(Statement):
    """Спецификация типа: type T underlying_type"""
    def __init__(self, name: str, type_node: BaseType, line: int, col: int):
        self.name = name
        self.type_node = type_node
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_type_spec(self)

class AssignStatement(Statement):
    """Присваивание: x = y или x, y = fn()"""
    def __init__(self, targets: List[ASTNode], values: List[ASTNode], line: int, col: int):
        self.targets = targets
        self.values = values
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_assign_statement(self)

class IfStatement(Statement):
    """Условный оператор: if cond { ... } else { ... }"""
    def __init__(self, init: Optional[Statement], condition: ASTNode, 
                 consequence: BlockStatement, alternative: Optional[Statement], 
                 line: int, col: int):
        self.init = init 
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_if_statement(self)

class SwitchStatement(Statement):
    """Оператор switch: switch tag { case ... }"""
    def __init__(self, init: Optional[Statement], tag: Optional[ASTNode], 
                 cases: List['CaseClause'], line: int, col: int):
        self.init = init
        self.tag = tag 
        self.cases = cases
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_switch_statement(self)

class TypeSwitchStatement(Statement):
    """Type switch: switch v := x.(type) { case T: ... }"""
    def __init__(self, init: Optional[Statement], assign: Optional[AssignStatement], 
                 cases: List['CaseClause'], line: int, col: int):
        self.init = init
        self.assign = assign  
        self.cases = cases
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_type_switch_statement(self)

class CaseClause(Statement):
    """Ветка case в switch: case expr1, expr2: body"""
    def __init__(self, exprs: List[ASTNode], body: List[Statement], line: int, col: int):
        self.exprs = exprs 
        self.body = body
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_case_clause(self)

class SelectStatement(Statement):
    """Select для каналов: select { case ch <- val: ... case x := <-ch: ... default: ... }"""
    def __init__(self, cases: List['CommClause'], line: int, col: int):
        self.cases = cases
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_select_statement(self)

class CommClause(Statement):
    """Ветка case в select: case ch <- val: body"""
    def __init__(self, comm: Optional[Statement], body: List[Statement], line: int, col: int):
        self.comm = comm 
        self.body = body
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_case_clause(CaseClause(
            [self.comm] if self.comm else [], self.body, self.line, self.col))

class ForStatement(Statement):
    """Цикл for: for init; cond; post { ... }"""
    def __init__(self, init: Optional[Statement], cond: Optional[ASTNode], 
                 post: Optional[Statement], body: BlockStatement, line: int, col: int):
        self.init = init
        self.cond = cond
        self.post = post
        self.body = body
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_for_statement(self)

class ForRangeStatement(Statement):
    """Range цикл: for key, val := range expr { ... }"""
    def __init__(self, key: Optional[str], value: Optional[str], 
                 expr: ASTNode, body: BlockStatement, line: int, col: int):
        self.key = key
        self.value = value
        self.expr = expr
        self.body = body
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_for_range_statement(self)

class ReturnStatement(Statement):
    """Оператор return: return expr1, expr2"""
    def __init__(self, results: List[ASTNode], line: int, col: int):
        self.results = results
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_return_statement(self)

class DeferStatement(Statement):
    """Отложенный вызов: defer fn()"""
    def __init__(self, call: CallExpression, line: int, col: int):
        self.call = call
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_defer_statement(self)

class GoStatement(Statement):
    """Запуск горутины: go fn()"""
    def __init__(self, call: CallExpression, line: int, col: int):
        self.call = call
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_go_statement(self)


class BreakStatement(Statement):
    """Оператор break: break label"""
    def __init__(self, label: Optional[str], line: int, col: int):
        self.label = label
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_break_statement(self)

class ContinueStatement(Statement):
    """Оператор continue: continue label"""
    def __init__(self, label: Optional[str], line: int, col: int):
        self.label = label
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_continue_statement(self)

class GotoStatement(Statement):
    """Оператор goto: goto label"""
    def __init__(self, label: str, line: int, col: int):
        self.label = label
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_goto_statement(self)

class LabelStatement(Statement):
    """Объявление метки: Label:"""
    def __init__(self, label: str, stmt: Statement, line: int, col: int):
        self.label = label
        self.stmt = stmt
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_label_statement(self)


class PackageDeclaration(Statement):
    """Объявление пакета: package main"""
    def __init__(self, name: str, line: int, col: int):
        self.name = name
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_package_declaration(self)

class ImportDeclaration(Statement):
    def __init__(self, path: str, alias: Optional[str] = None, line: int = -1, col: int = -1):
        self.path = path
        self.alias = alias
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_import_declaration(self)

class FuncDeclaration(Statement):
    """Объявление функции: func name(params) returns { body }"""
    def __init__(self, name: str, receiver: Optional[Parameter], 
                 params: List[Parameter], returns: List[BaseType], 
                 body: BlockStatement, line: int, col: int):
        self.name = name
        self.receiver = receiver  
        self.params = params
        self.returns = returns
        self.body = body
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return visitor.visit_func_declaration(self)

class EmptyStatement(Statement):
    """Пустой оператор: ;"""
    def __init__(self, line: int = -1, col: int = -1):
        self.line = line
        self.col = col

    def accept(self, visitor: Visitor):
        return None 