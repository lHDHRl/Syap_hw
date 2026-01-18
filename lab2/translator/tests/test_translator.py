import pytest
from lexer.tokenizer import GoLexer
from parser.go_parser import GoParser
from translator.python_emitter import PythonEmitter


def translate_go_to_python(go_code: str) -> str:
    """Helper функция для трансляции Go кода в Python"""
    lexer = GoLexer(go_code)
    tokens = lexer.tokenize()
    parser = GoParser(tokens)
    ast = parser.parse()
    emitter = PythonEmitter()
    return emitter.translate(ast)


def test_simple_function_translation():
    """Тест трансляции простой функции"""
    go_code = """
    func hello() {
        return
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "def hello():" in python_code
    assert "return" in python_code


def test_function_with_println():
    """Тест трансляции fmt.Println"""
    go_code = """
    package main
    
    import "fmt"
    
    func main() {
        fmt.Println("Hello, World!")
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "def main():" in python_code
    assert 'print("Hello, World!")' in python_code


def test_defer_translation():
    """
    КОНСТРУКЦИЯ #1: Тест трансляции defer statement
    
    defer - уникальная фича Go, которая откладывает выполнение функции
    до выхода из текущей функции. В Python эмулируется через try-finally.
    """
    go_code = """
    func cleanup() {
        defer closeFile()
        doSomething()
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "def cleanup():" in python_code
    assert "try:" in python_code
    assert "finally:" in python_code
    assert "doSomething()" in python_code
    assert "closeFile()" in python_code


def test_goroutine_translation():
    """
    КОНСТРУКЦИЯ #2: Тест трансляции go statement (goroutines)
    
    go - уникальная фича Go для создания горутин (легковесных потоков).
    В Python транслируется в threading.Thread
    """
    go_code = """
    func main() {
        go doWork()
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "import threading" in python_code
    assert "threading.Thread" in python_code
    assert "target=doWork" in python_code
    assert ".start()" in python_code


def test_for_range_translation():
    """
    КОНСТРУКЦИЯ #3: Тест трансляции for-range loop
    
    for range - конструкция Go для итерации с индексами.
    В Python транслируется в enumerate() или range()
    """
    go_code = """
    func iterate() {
        for i, v := range items {
            process(i, v)
        }
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "def iterate():" in python_code
    assert "for i, v in enumerate(items):" in python_code
    assert "process(i, v)" in python_code


def test_for_range_key_only():
    """Тест трансляции for range только с ключом"""
    go_code = """
    func iterate() {
        for i := range items {
            process(i)
        }
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "for i in range(len(items)):" in python_code


def test_if_statement_translation():
    """Тест трансляции if statement"""
    go_code = """
    func check(x int) {
        if x > 0 {
            return true
        } else {
            return false
        }
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "if x > 0:" in python_code
    assert "else:" in python_code
    assert "return True" in python_code
    assert "return False" in python_code


def test_binary_operators():
    """Тест трансляции бинарных операторов"""
    go_code = """
    func logic() {
        if x && y {
            return true
        }
        if a || b {
            return false
        }
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "x and y" in python_code
    assert "a or b" in python_code


def test_short_variable_declaration():
    """Тест трансляции := оператора"""
    go_code = """
    func assign() {
        x := 42
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "x = 42" in python_code


def test_struct_translation():
    """Тест трансляции struct в Python class"""
    go_code = """
    type Person struct {
        Name string
        Age int
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "class Person:" in python_code
    assert "def __init__(self, Name, Age):" in python_code
    assert "self.Name = Name" in python_code
    assert "self.Age = Age" in python_code


def test_complex_defer():
    """Тест множественных defer вызовов"""
    go_code = """
    func process() {
        defer cleanup1()
        defer cleanup2()
        doWork()
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "try:" in python_code
    assert "finally:" in python_code
    assert "cleanup1()" in python_code
    assert "cleanup2()" in python_code
    
    cleanup1_pos = python_code.index("cleanup1()")
    cleanup2_pos = python_code.index("cleanup2()")
    finally_pos = python_code.index("finally:")
    
    if cleanup1_pos > finally_pos and cleanup2_pos > finally_pos:
        assert cleanup2_pos < cleanup1_pos


def test_anonymous_goroutine():
    """Тест трансляции анонимной функции в горутине"""
    go_code = """
    func main() {
        go func() {
            fmt.Println("In goroutine")
        }()
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "import threading" in python_code
    assert "threading.Thread" in python_code
    assert 'print("In goroutine")' in python_code


def test_full_program():
    """Тест трансляции полной программы"""
    go_code = """
    package main

    import "fmt"

    func hello() {
        fmt.Println("Hello, world!")
    }

    func main() {
        defer hello()
        go func() {
            fmt.Println("Goroutine!")
        }()
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "import threading" in python_code
    assert "def hello():" in python_code
    assert "def main():" in python_code
    assert 'print("Hello, world!")' in python_code
    assert 'print("Goroutine!")' in python_code
    assert "try:" in python_code
    assert "finally:" in python_code
    assert "threading.Thread" in python_code


def test_var_declaration():
    """Тест трансляции объявления переменных"""
    go_code = """
    func vars() {
        var x int
        var y int = 42
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "x = None" in python_code
    assert "y = 42" in python_code


def test_return_with_expression():
    """Тест трансляции return с выражением"""
    go_code = """
    func add(a int, b int) int {
        return a + b
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "def add(a, b):" in python_code
    assert "return a + b" in python_code


def test_unary_operators():
    """Тест трансляции унарных операторов"""
    go_code = """
    func logic() {
        if !condition {
            return
        }
    }
    """
    
    python_code = translate_go_to_python(go_code)
    
    assert "if not condition:" in python_code