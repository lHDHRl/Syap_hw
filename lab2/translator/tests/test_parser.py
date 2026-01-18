import pytest
from lexer.tokenizer import GoLexer
from parser.go_parser import GoParser
from parser.ast_nodes import (
    FuncDeclaration, VarDeclaration, IfStatement, ForRangeStatement,
    ReturnStatement, DeferStatement, GoStatement, CallExpression,
    Identifier, Literal, BinaryOp, PackageDeclaration, ImportDeclaration, MemberAccess
)


def test_package_declaration():
    """Тест объявления package"""
    code = "package main"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    assert isinstance(ast[0], PackageDeclaration)
    assert ast[0].name == "main"


def test_import_declaration():
    """Тест объявления import"""
    code = 'package main\nimport "fmt"'
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 2
    assert isinstance(ast[0], PackageDeclaration)
    assert isinstance(ast[1], ImportDeclaration)
    assert ast[1].path == '"fmt"'


def test_simple_function():
    """Тест простой функции"""
    code = """
    func hello() {
        return
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    assert isinstance(ast[0], FuncDeclaration)
    assert ast[0].name == "hello"
    assert len(ast[0].params) == 0
    assert len(ast[0].returns) == 0


def test_function_with_parameters():
    """Тест функции с параметрами"""
    code = """
    func add(x int, y int) int {
        return x + y;
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    assert isinstance(func, FuncDeclaration)
    assert func.name == "add"
    assert len(func.params) == 2
    assert func.params[0].name == "x"
    assert func.params[1].name == "y"
    assert len(func.returns) == 1


def test_member_access():
    """Тест доступа к членам (fmt.Println)"""
    code = """
    func main() {
        fmt.Println("Hello");
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    assert isinstance(func, FuncDeclaration)
    
    call_stmt = func.body.statements[0]
    assert isinstance(call_stmt, CallExpression)
    assert isinstance(call_stmt.func, MemberAccess)
    assert isinstance(call_stmt.func.obj, Identifier)
    assert call_stmt.func.obj.name == "fmt"
    assert call_stmt.func.member == "Println"


def test_defer_statement():
    """Тест defer statement"""
    code = """
    func main() {
        defer fmt.Println("Goodbye");
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    defer_stmt = func.body.statements[0]
    assert isinstance(defer_stmt, DeferStatement)
    assert isinstance(defer_stmt.call, CallExpression)


def test_go_statement():
    """Тест go statement (goroutine)"""
    code = """
    func main() {
        go sayHello();
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    go_stmt = func.body.statements[0]
    assert isinstance(go_stmt, GoStatement)
    assert isinstance(go_stmt.call, CallExpression)


def test_anonymous_function():
    """Тест анонимной функции"""
    code = """
    func main() {
        go func() {
            fmt.Println("In goroutine");
        }();
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    go_stmt = func.body.statements[0]
    assert isinstance(go_stmt, GoStatement)
    
    call = go_stmt.call
    assert isinstance(call, CallExpression)
    assert isinstance(call.func, FuncDeclaration)
    assert call.func.name == ""  # Анонимная функция


def test_if_statement():
    """Тест if statement"""
    code = """
    func main() {
        if x > 0 {
            fmt.Println("Positive");
        }
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.condition, BinaryOp)
    assert if_stmt.condition.operator == ">"


def test_if_else_statement():
    """Тест if-else statement"""
    code = """
    func main() {
        if x > 0 {
            fmt.Println("Positive");
        } else {
            fmt.Println("Non-positive");
        }
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStatement)
    assert if_stmt.alternative is not None


def test_for_range_statement():
    """Тест for range statement"""
    code = """
    func main() {
        for i, v := range items {
            fmt.Println(i, v);
        }
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    for_stmt = func.body.statements[0]
    assert isinstance(for_stmt, ForRangeStatement)
    assert for_stmt.key == "i"
    assert for_stmt.value == "v"


def test_var_declaration():
    """Тест объявления переменной"""
    code = """
    func main() {
        var x int
        var y int = 42
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    
    var1 = func.body.statements[0]
    assert isinstance(var1, VarDeclaration)
    assert var1.names[0] == "x"
    
    var2 = func.body.statements[1]
    assert isinstance(var2, VarDeclaration)
    assert var2.names[0] == "y"
    assert isinstance(var2.values[0], Literal)


def test_short_variable_declaration():
    """Тест короткого объявления переменной"""
    code = """
    func main() {
        x := 42;
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    
    assign = func.body.statements[0]
    assert isinstance(assign, BinaryOp)
    assert assign.operator == ":="


def test_comments_ignored():
    """Тест игнорирования комментариев"""
    code = """
    // This is a line comment
    func main() {
        /* This is a
           block comment */
        fmt.Println("Hello");
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    assert isinstance(ast[0], FuncDeclaration)


def test_full_program():
    """Тест полной программы из test.go"""
    with open('tests/test.go', 'r') as f:
        source_code = f.read()
    
    lexer = GoLexer(source_code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) >= 4  
    
    functions = [node for node in ast if isinstance(node, FuncDeclaration)]
    assert len(functions) == 2
    
    func_names = [f.name for f in functions]
    assert "hello" in func_names
    assert "main" in func_names
    
    hello_func = next(f for f in functions if f.name == "hello")
    assert len(hello_func.body.statements) == 1  
    
    main_func = next(f for f in functions if f.name == "main")
    assert len(main_func.body.statements) == 2 
    
    defer_stmt = main_func.body.statements[0]
    assert isinstance(defer_stmt, DeferStatement)
    
    go_stmt = main_func.body.statements[1]
    assert isinstance(go_stmt, GoStatement)


def test_binary_operations():
    """Тест бинарных операций"""
    code = """
    func calc() int {
        return 2 + 3 * 4;
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    ret_stmt = func.body.statements[0]
    assert isinstance(ret_stmt, ReturnStatement)
    assert isinstance(ret_stmt.expr, BinaryOp)


def test_function_call_with_multiple_args():
    """Тест вызова функции с несколькими аргументами"""
    code = """
    func main() {
        fmt.Printf("%d %d", 1, 2);
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    call = func.body.statements[0]
    assert isinstance(call, CallExpression)
    assert len(call.args) == 3  


def test_nested_function_calls():
    """Тест вложенных вызовов функций"""
    code = """
    func main() {
        fmt.Println(getString());
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    outer_call = func.body.statements[0]
    assert isinstance(outer_call, CallExpression)
    assert len(outer_call.args) == 1
    inner_call = outer_call.args[0]
    assert isinstance(inner_call, CallExpression)


def test_literal_types():
    """Тест различных типов литералов"""
    code = """
    func main() {
        var a int = 42;
        var b float = 3.14;
        var c string = "hello";
        var d bool = true;
        var e bool = false;
    }
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    
    assert len(ast) == 1
    func = ast[0]
    
    assert isinstance(func.body.statements[0].values[0], Literal)
    assert func.body.statements[0].values[0].value == 42
    
    assert isinstance(func.body.statements[1].values[0], Literal)
    assert func.body.statements[1].values[0].value == 3.14
    
    assert isinstance(func.body.statements[2].values[0], Literal)
    assert '"hello"' in func.body.statements[2].values[0].value
    
    assert isinstance(func.body.statements[3].values[0], Literal)
    assert func.body.statements[3].values[0].value == True
    
    assert isinstance(func.body.statements[4].values[0], Literal)
    assert func.body.statements[4].values[0].value == False