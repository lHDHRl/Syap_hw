import pytest
from lexer.tokenizer import GoLexer
from lexer.tokens import TokenType

def test_simple_package_declaration():
    code = "package main"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.PACKAGE,
        TokenType.IDENT,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[1].value == "main"

def test_import_statement():
    code = 'import "fmt"'
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.IMPORT,
        TokenType.STRING,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[1].value == '"fmt"'

def test_short_variable_declaration():
    code = "x := 42"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.IDENT,
        TokenType.DEFINE,
        TokenType.INT,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[0].value == "x"
    assert tokens[2].value == "42"

def test_function_declaration():
    code = "func hello() { }"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.FUNC,
        TokenType.IDENT,
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE,
        TokenType.RIGHT_BRACE,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[1].value == "hello"

def test_struct_declaration():
    code = "type Person struct { Name string }"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.TYPE,
        TokenType.IDENT,
        TokenType.STRUCT,
        TokenType.LEFT_BRACE,
        TokenType.IDENT,
        TokenType.IDENT,
        TokenType.RIGHT_BRACE,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[1].value == "Person"
    assert tokens[4].value == "Name"
    assert tokens[5].value == "string"

def test_interface_declaration():
    code = "type Reader interface { Read() []byte }"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.TYPE,
        TokenType.IDENT,
        TokenType.INTERFACE,
        TokenType.LEFT_BRACE,
        TokenType.IDENT,
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACKET,
        TokenType.RIGHT_BRACKET,
        TokenType.IDENT,
        TokenType.RIGHT_BRACE,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[1].value == "Reader"
    assert tokens[4].value == "Read"
    assert tokens[9].value == "byte"

def test_channel_and_go_keyword():
    code = "go sendData(ch <-chan int)"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.GO,
        TokenType.IDENT,
        TokenType.LEFT_PAREN,
        TokenType.IDENT,
        TokenType.ARROW,
        TokenType.CHAN,
        TokenType.IDENT,
        TokenType.RIGHT_PAREN,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[1].value == "sendData"
    assert tokens[3].value == "ch"

def test_defer_and_multiline_comment():
    code = """
    // This is a line comment
    /*
    block comment
    */
    defer fmt.Println()
    """
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    comment_types = [TokenType.COMMENT, TokenType.COMMENT]
    main_tokens = [
        TokenType.DEFER,
        TokenType.IDENT,
        TokenType.DOT,
        TokenType.IDENT,
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.EOF,
    ]

    assert len([t for t in tokens if t.type == TokenType.COMMENT]) == 2
    non_comment_tokens = [t for t in tokens if t.type != TokenType.COMMENT]
    assert [t.type for t in non_comment_tokens] == main_tokens

def test_raw_string_literal():
    code = 'msg := `Hello\nWorld`'
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected = [
        TokenType.IDENT,
        TokenType.DEFINE,
        TokenType.STRING,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected
    assert tokens[2].value == '`Hello\nWorld`'

def test_float_literal():
    code = "pi := 3.1415"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    assert tokens[2].type == TokenType.FLOAT
    assert tokens[2].value == "3.1415"

def test_method_with_receiver():
    code = "func (p *Person) GetName() string"
    lexer = GoLexer(code)
    tokens = lexer.tokenize()

    expected_types = [
        TokenType.FUNC,
        TokenType.LEFT_PAREN,
        TokenType.IDENT,
        TokenType.ASTERISK,
        TokenType.IDENT,
        TokenType.RIGHT_PAREN,
        TokenType.IDENT,
        TokenType.LEFT_PAREN,
        TokenType.RIGHT_PAREN,
        TokenType.IDENT,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types
    assert tokens[2].value == "p"
    assert tokens[4].value == "Person"
    assert tokens[6].value == "GetName"
    assert tokens[9].value == "string"