import re
from typing import List, Optional
from .tokens import TokenType

KEYWORDS = {
    "package": TokenType.PACKAGE,
    "import": TokenType.IMPORT,
    "func": TokenType.FUNC,
    "struct": TokenType.STRUCT,
    "interface": TokenType.INTERFACE,
    "type": TokenType.TYPE,
    "var": TokenType.VAR,
    "const": TokenType.CONST,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "range": TokenType.RANGE,
    "return": TokenType.RETURN,
    "defer": TokenType.DEFER,
    "go": TokenType.GO,
    "chan": TokenType.CHAN,
    "map": TokenType.MAP,
    "select": TokenType.SELECT,
    "switch": TokenType.SWITCH,
    "case": TokenType.CASE,
    "default": TokenType.DEFAULT,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "goto": TokenType.GOTO,
    "fallthrough": TokenType.FALLTHROUGH,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nil": TokenType.NIL,
    "caret": TokenType.CARET,
    "_": TokenType.UNDERSCORE,
}

class Token:
    __slots__ = ("type", "value", "line", "column")
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class GoLexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        return char

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _add_token(self, type_: TokenType, value: Optional[str] = None):
        if value is None:
            value = self.source[self.start:self.current]
        self.tokens.append(Token(type_, value, self.line, self.column - (self.current - self.start)))

    def _scan_token(self):
        char = self._advance()
        if char == ' ' or char == '\t' or char == '\r':
            return
        elif char == '\n':
            return
        elif char == '"':
            self._string('"')
        elif char == '`':
            self._raw_string()
        elif char == '/':
            if self._peek() == '/':
                self._line_comment()
            elif self._peek() == '*':
                self._block_comment()
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.SLASH_ASSIGN)
            else:
                self._add_token(TokenType.SLASH)
        elif char == ':':
            if self._peek() == '=':
                self._advance()
                self._add_token(TokenType.DEFINE)
            else:
                self._add_token(TokenType.COLON)
        elif char == '<':
            if self._peek() == '<':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    self._add_token(TokenType.SHIFT_LEFT_ASSIGN)
                else:
                    self._add_token(TokenType.SHIFT_LEFT)
            elif self._peek() == '-':
                self._advance()
                self._add_token(TokenType.ARROW)
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.LTE)
            else:
                self._add_token(TokenType.LT)
        elif char == '>':
            if self._peek() == '>':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    self._add_token(TokenType.SHIFT_RIGHT_ASSIGN)
                else:
                    self._add_token(TokenType.SHIFT_RIGHT)
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.GTE)
            else:
                self._add_token(TokenType.GT)
        elif char == '=':
            if self._peek() == '=':
                self._advance()
                self._add_token(TokenType.EQ)
            else:
                self._add_token(TokenType.ASSIGN)
        elif char == '!':
            if self._peek() == '=':
                self._advance()
                self._add_token(TokenType.NOT_EQ)
            else:
                self._add_token(TokenType.BANG)
        elif char == '&':
            if self._peek() == '&':
                self._advance()
                self._add_token(TokenType.AND)
            elif self._peek() == '^':
                self._advance()
                if self._peek() == '=':
                    self._advance()
                    self._add_token(TokenType.AND_NOT_ASSIGN)
                else:
                    self._add_token(TokenType.BIT_CLEAR)
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.AMP_ASSIGN)
            else:
                self._add_token(TokenType.AMPERSAND)
        elif char == '|':
            if self._peek() == '|':
                self._advance()
                self._add_token(TokenType.OR)
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.OR_ASSIGN)
            else:
                self._add_token(TokenType.BIT_OR)
        elif char == '^':
            if self._peek() == '=':
                self._advance()
                self._add_token(TokenType.CARET_ASSIGN)
            else:
                self._add_token(TokenType.BIT_XOR)
        elif char == '+':
            if self._peek() == '+':
                self._advance()
                self._add_token(TokenType.PLUS_PLUS)
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.PLUS_ASSIGN)
            else:
                self._add_token(TokenType.PLUS)
        elif char == '-':
            if self._peek() == '-':
                self._advance()
                self._add_token(TokenType.MINUS_MINUS)
            elif self._peek() == '=':
                self._advance()
                self._add_token(TokenType.MINUS_ASSIGN)
            else:
                self._add_token(TokenType.MINUS)
        elif char == '*':
            if self._peek() == '=':
                self._advance()
                self._add_token(TokenType.STAR_ASSIGN)
            else:
                self._add_token(TokenType.ASTERISK)
        elif char == '%':
            if self._peek() == '=':
                self._advance()
                self._add_token(TokenType.PERCENT_ASSIGN)
            else:
                self._add_token(TokenType.PERCENT)
        elif char == '.':
            if self._peek() == '.' and self._peek_next() == '.':
                self._advance() 
                self._advance()  
                self._add_token(TokenType.ELLIPSIS)
            else:
                self._add_token(TokenType.DOT)
        elif char.isdigit():
            self._number()
        elif char.isalpha() or char == '_':
            self._identifier()
        else:
            self._handle_simple_tokens(char)

    def _string(self, quote: str):
        while not self._is_at_end() and self._peek() != quote:
            if self._peek() == '\n':
                break
            self._advance()
        if self._is_at_end():
            raise SyntaxError(f"Unterminated string at line {self.line}")
        self._advance()
        value = self.source[self.start+1:self.current-1]
        self._add_token(TokenType.STRING, value)

    def _raw_string(self):
        while not self._is_at_end() and self._peek() != '`':
            self._advance()
        if self._is_at_end():
            raise SyntaxError(f"Unterminated raw string at line {self.line}")
        self._advance()
        value = self.source[self.start+1:self.current-1]
        self._add_token(TokenType.STRING, value)

    def _line_comment(self):
        self._advance()
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()
        self._add_token(TokenType.COMMENT)

    def _block_comment(self):
        self._advance()  
        while not (self._peek() == '*' and self._peek_next() == '/'):
            if self._is_at_end():
                raise SyntaxError(f"Unterminated block comment at line {self.line}")
            self._advance()
        self._advance()  
        self._advance()  
        self._add_token(TokenType.COMMENT)

    def _number(self):
        while self._peek().isdigit():
            self._advance()
        if self._peek() == '.' and self._peek_next().isdigit():
            self._advance()  
            while self._peek().isdigit():
                self._advance()
            self._add_token(TokenType.FLOAT)
        else:
            self._add_token(TokenType.INT)

    def _identifier(self):
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()
        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENT)
        self._add_token(token_type, text)

    def _handle_simple_tokens(self, char: str):
        mapping = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
        }
        if char in mapping:
            self._add_token(mapping[char])
        elif char == '_':
            self._add_token(TokenType.UNDERSCORE)
        else:
            raise SyntaxError(f"Unexpected character: {char} at line {self.line}")