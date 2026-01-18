# go_parser.py
from typing import List, Optional, Any, Union
from lexer.tokens import TokenType
from lexer.tokenizer import Token
from parser.ast_nodes import (
    ASTNode, Statement, BaseType, BasicType,
    StructType, ChanType, Field, Parameter,
    BinaryOp, UnaryOp, CallExpression, MemberAccess, CompositeLiteral, KeyValueExpr,
    ChannelOperation,
    BlockStatement, ExprStatement, VarDeclaration, ConstDeclaration, TypeSpec,
    IfStatement, ForRangeStatement,
    ReturnStatement, DeferStatement, GoStatement,
    PackageDeclaration, ImportDeclaration, FuncDeclaration,
    EmptyStatement, Literal, Identifier, Visitor
)

class ParseError(Exception):
    def __init__(self, message: str, token: Optional[Token] = None):
        if token:
            message = f"{message} at line {token.line}, col {token.column}"
        super().__init__(message)
        self.token = token

class GoParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = []
        for token in tokens:
            if token.type == TokenType.COMMENT:
                continue
            if not hasattr(token, 'type') or not hasattr(token, 'value'):
                raise ParseError(f"Invalid token object detected")
            self.tokens.append(token)
        self.current = 0

    def parse(self) -> List[ASTNode]:
        """Основной метод парсинга - возвращает список узлов верхнего уровня"""
        statements = []
        try:
            while not self._is_at_end():
                stmt = self._top_level_declaration()
                if stmt:
                    statements.append(stmt)
        except ParseError as e:
            print(f"Parse error: {str(e)}")
            raise
        return statements

    def _top_level_declaration(self) -> Optional[ASTNode]:
        """Парсим объявления верхнего уровня: package, import, func, type, var, const"""
        if self._match(TokenType.PACKAGE):
            return self._package_declaration()
        if self._match(TokenType.IMPORT):
            return self._import_declaration()
        if self._match(TokenType.TYPE):
            return self._type_declaration()
        if self._match(TokenType.VAR):
            return self._var_declaration()
        if self._match(TokenType.CONST):
            return self._const_declaration()
        if self._check(TokenType.FUNC):
            return self._function_declaration()
        
        if not self._is_at_end():
            return self._statement()
        return None

    def _package_declaration(self) -> PackageDeclaration:
        line = self._previous().line
        col = self._previous().column
        name_token = self._consume(TokenType.IDENT, "Expected package name after 'package'")
        return PackageDeclaration(name_token.value, line, col)

    def _import_declaration(self) -> ImportDeclaration:
        line = self._previous().line
        col = self._previous().column
        
        if self._match(TokenType.LEFT_BRACE):
            imports = []
            while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
                if self._match(TokenType.STRING):
                    path = self._previous().value
                    alias = None
                    if self._check(TokenType.IDENT):
                        alias_token = self._advance()
                        self._consume(TokenType.STRING, "Expected import path after alias")
                        path = self._previous().value
                        alias = alias_token.value
                    imports.append(ImportDeclaration(path.strip('"'), alias, alias_token.line, alias_token.column))
                else:
                    self._advance()
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' to end import group")
            return imports[0] if imports else None
        
        alias = None
        if self._check(TokenType.IDENT):
            alias_token = self._advance()
            alias = alias_token.value
        path_token = self._consume(TokenType.STRING, "Expected import path")
        path = path_token.value.strip('"')
        return ImportDeclaration(path, alias, line, col)

    def _type_declaration(self) -> TypeSpec:
        line = self._previous().line
        col = self._previous().column
        name_token = self._consume(TokenType.IDENT, "Expected type name after 'type'")
        name = name_token.value
        type_node = self._parse_type()
        return TypeSpec(name, type_node, line, col)

    def _parse_type(self) -> BaseType:
        """Парсим любой тип данных в Go"""
        line = self._peek().line
        col = self._peek().column
        
        if self._match(TokenType.STRUCT):
            return self._struct_type()

        if self._match(TokenType.CHAN):
            elem_type = self._parse_type()
            return ChanType("both", elem_type, line, col)
        
        if self._match(TokenType.IDENT):
            return BasicType(self._previous().value, line, col)
        
        raise ParseError(f"Unexpected token in type declaration: {self._peek().type}", self._peek())

    def _struct_type(self) -> StructType:
        """Парсим структурный тип: struct { fields }"""
        line = self._previous().line
        col = self._previous().column
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'struct'")
        
        fields = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            names = []
            if self._check(TokenType.IDENT):
                while True:
                    name_token = self._consume(TokenType.IDENT, "Expected field name")
                    names.append(name_token.value)
                    if not self._match(TokenType.COMMA):
                        break
            
            field_type = self._parse_type()
            tag = None
            if self._match(TokenType.STRING):
                tag = self._previous().value.strip('`"')
            
            fields.append(Field(names, field_type, tag, self._previous().line, self._previous().column))
            self._match(TokenType.SEMICOLON)
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' to end struct")
        return StructType(None, fields, line, col)



    def _parse_return_types(self) -> List[BaseType]:
        """Парсим возвращаемые типы функции"""
        returns = []
        if self._match(TokenType.LEFT_PAREN):
            while not self._check(TokenType.RIGHT_PAREN) and not self._is_at_end():
                returns.append(self._parse_type())
                self._match(TokenType.COMMA)
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after return types")
        else:
            returns.append(self._parse_type())
        return returns

    def _var_declaration(self) -> VarDeclaration:
        """Парсим объявление переменной: var x T = val или x := val"""
        line = self._previous().line
        col = self._previous().column
        
        names = []
        types = []
        values = []
        is_short = False
        
        while True:
            if not self._check(TokenType.IDENT):
                raise ParseError("Expected variable name", self._peek())
            name_token = self._advance()
            names.append(name_token.value)
            
            if not self._match(TokenType.COMMA):
                break
        
        if self._match(TokenType.DEFINE):
            is_short = True
        else:
            if self._check(TokenType.IDENT) or self._check(TokenType.LEFT_BRACKET) or self._check(TokenType.MAP) or self._check(TokenType.STRUCT) or self._check(TokenType.INTERFACE) or self._check(TokenType.FUNC) or self._check(TokenType.CHAN):
                while True:
                    types.append(self._parse_type())
                    if not self._match(TokenType.COMMA):
                        break
            
            if self._match(TokenType.ASSIGN):
                while True:
                    values.append(self._expression())
                    if not self._match(TokenType.COMMA):
                        break
        
        self._match(TokenType.SEMICOLON)
        
        return VarDeclaration(names, types, values, is_short, line, col)

    def _const_declaration(self) -> ConstDeclaration:
        """Парсим объявление константы: const x = 42"""
        line = self._previous().line
        col = self._previous().column
        
        names = []
        types = []
        values = []
        
        while True:
            if not self._check(TokenType.IDENT):
                raise ParseError("Expected constant name", self._peek())
            name_token = self._advance()
            names.append(name_token.value)
            
            if not self._match(TokenType.COMMA):
                break
        
        if self._check(TokenType.IDENT) or self._check(TokenType.LEFT_BRACKET) or self._check(TokenType.MAP) or self._check(TokenType.STRUCT) or self._check(TokenType.INTERFACE) or self._check(TokenType.FUNC) or self._check(TokenType.CHAN):
            while True:
                types.append(self._parse_type())
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.ASSIGN, "Expected '=' after const declaration")
        
        while True:
            values.append(self._expression())
            if not self._match(TokenType.COMMA):
                break
        
        self._match(TokenType.SEMICOLON)
        
        return ConstDeclaration(names, types, values, line, col)

    def _function_declaration(self) -> FuncDeclaration:
        """Парсим объявление функции: func name(params) returns { body }"""
        self._consume(TokenType.FUNC, "Expected 'func'")
        line = self._previous().line
        col = self._previous().column
        
        receiver = None
        if self._check(TokenType.LEFT_PAREN):
            self._advance()  # '('
            if self._check(TokenType.IDENT):
                recv_name = self._consume(TokenType.IDENT, "Expected receiver name").value
                
                recv_type = self._parse_type()
                
                receiver = Parameter([recv_name], recv_type, self._previous().line, self._previous().column)
                self._consume(TokenType.RIGHT_PAREN, "Expected ')' after receiver")
        
        name_token = self._consume(TokenType.IDENT, "Expected function name")
        name = name_token.value
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        params = self._parameters()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        
        returns = []
        if not self._check(TokenType.LEFT_BRACE):
            returns = self._parse_return_types()
        
        body = self._block_statement()
        
        return FuncDeclaration(name, receiver, params, returns, body, line, col)

    def _parameters(self) -> List[Parameter]:
        """Парсим параметры функции"""
        params = []
        if self._check(TokenType.RIGHT_PAREN):
            return params
        
        while True:
            names = []
            if self._check(TokenType.IDENT):
                while True:
                    name_token = self._consume(TokenType.IDENT, "Expected parameter name")
                    names.append(name_token.value)
                    if not self._match(TokenType.COMMA):
                        break
            
            param_type = self._parse_type()
            params.append(Parameter(names, param_type, self._previous().line, self._previous().column))
            
            if not self._match(TokenType.COMMA):
                break
        
        return params

    def _statement(self) -> Statement:
        """Парсим любой оператор"""
        if self._match(TokenType.LEFT_BRACE):
            self.current -= 1
            return self._block_statement()
        
        if self._match(TokenType.VAR):
            self.current -= 1
            return self._var_declaration()
        if self._match(TokenType.CONST):
            self.current -= 1
            return self._const_declaration()
        if self._match(TokenType.TYPE):
            self.current -= 1
            return self._type_declaration()
        
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.DEFER):
            return self._defer_statement()
        if self._match(TokenType.GO):
            return self._go_statement()
        
        
        expr = self._expression()
        self._match(TokenType.SEMICOLON)
        return ExprStatement(expr, expr.line, expr.col)

    def _block_statement(self) -> BlockStatement:
        """Парсим блок операторов: { ... }"""
        line = self._peek().line
        col = self._peek().column
        self._consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        statements = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return BlockStatement(statements, line, col)

    def _if_statement(self) -> IfStatement:
        """Парсим условный оператор: if init; cond { ... } else { ... }"""
        line = self._previous().line
        col = self._previous().column
        
        init = None
        if self._check(TokenType.IDENT) and self._peek_ahead().type in (TokenType.DEFINE, TokenType.ASSIGN):
            init = self._statement()
            self._consume(TokenType.SEMICOLON, "Expected ';' after if initialization")
        
        condition = self._expression()
        
        consequence = self._block_statement()
        

        alternative = None
        if self._match(TokenType.ELSE):
            if self._check(TokenType.IF):
                alternative = self._if_statement()
            else:
                alternative = self._block_statement()
        
        return IfStatement(init, condition, consequence, alternative, line, col)



    def _for_statement(self) -> ForRangeStatement:
        """Парсим цикл for в любой форме"""
        line = self._previous().line
        col = self._previous().column
        
        if self._check(TokenType.IDENT) and (self._peek_ahead().type == TokenType.DEFINE or 
                                             (self._peek_ahead().type == TokenType.COMMA and 
                                              self._peek_ahead(2).type == TokenType.IDENT and 
                                              self._peek_ahead(3).type == TokenType.DEFINE)):
            return self._for_range_statement()
        
        init = None
        cond = None
        post = None
        
        if not self._check(TokenType.SEMICOLON):
            if self._check(TokenType.IDENT) and self._peek_ahead().type in (TokenType.DEFINE, TokenType.ASSIGN):
                init = self._statement()
            else:
                cond = self._expression()
        
        if self._match(TokenType.SEMICOLON):
            if not self._check(TokenType.SEMICOLON):
                cond = self._expression()
        
        if self._match(TokenType.SEMICOLON):
            if not self._check(TokenType.LEFT_BRACE):
                post = self._statement()
        
        body = self._block_statement()
        return ForStatement(init, cond, post, body, line, col)

    def _for_range_statement(self) -> ForRangeStatement:
        """Парсим range-цикл: for key, val := range expr { ... }"""
        
        key = None
        value = None
        
        if self._check(TokenType.IDENT):
            key = self._advance().value
            if self._match(TokenType.COMMA):
                if self._check(TokenType.IDENT):
                    value = self._advance().value
                else:
                    self._consume(TokenType.UNDERSCORE, "Expected value variable or '_'")
                    value = "_"
        
        self._consume(TokenType.DEFINE, "Expected ':=' in range statement")
        self._consume(TokenType.RANGE, "Expected 'range' keyword")
        
        expr = self._expression()
        body = self._block_statement()
        
        return ForRangeStatement(key, value, expr, body, self._previous().line, self._previous().column)

    def _return_statement(self) -> ReturnStatement:
        """Парсим оператор return"""
        line = self._previous().line
        col = self._previous().column
        results = []
        
   
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            while True:
                results.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        
        self._match(TokenType.SEMICOLON) 
        return ReturnStatement(results, line, col)

    def _go_statement(self) -> GoStatement:
        """Парсим запуск горутины: go fn() или go func() { ... }()"""
        line = self._previous().line
        col = self._previous().column
    

        expr = self._expression()
    

        if not isinstance(expr, CallExpression):
            raise ParseError("go statement requires a function call", self._previous())
    
        self._match(TokenType.SEMICOLON) 
        return GoStatement(expr, line, col)

    def _defer_statement(self) -> DeferStatement:
        """Парсим отложенный вызов: defer fn() или defer func() { ... }()"""
        line = self._previous().line
        col = self._previous().column
    
        expr = self._expression()
    
        if not isinstance(expr, CallExpression):
            raise ParseError("defer statement requires a function call", self._previous())
    
        self._match(TokenType.SEMICOLON)  
        return DeferStatement(expr, line, col)



    def _expression(self) -> ASTNode:
        """Точка входа для парсинга выражений"""
        return self._assignment()

    def _assignment(self) -> ASTNode:
        """Парсим присваивание: x = y или x := y"""
        expr = self._conditional()
        
        if self._match(TokenType.ASSIGN, TokenType.DEFINE, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN, TokenType.PERCENT_ASSIGN,
                      TokenType.AMP_ASSIGN, TokenType.OR_ASSIGN, TokenType.CARET_ASSIGN,
                      TokenType.SHIFT_LEFT_ASSIGN, TokenType.SHIFT_RIGHT_ASSIGN):
            op = self._previous().value
            value = self._assignment()
            return BinaryOp(expr, op, value, self._previous().line, self._previous().column)
        
        return expr

    def _conditional(self) -> ASTNode:
        """Парсим условное выражение: cond ? true_expr : false_expr (в Go нет тернарного оператора, но для будущего расширения)"""
        return self._logical_or()

    def _logical_or(self) -> ASTNode:
        """Парсим логическое ИЛИ: left || right"""
        expr = self._logical_and()
        while self._match(TokenType.OR):
            op = self._previous().value
            right = self._logical_and()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _logical_and(self) -> ASTNode:
        """Парсим логическое И: left && right"""
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous().value
            right = self._equality()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _equality(self) -> ASTNode:
        """Парсим операторы равенства: ==, !="""
        expr = self._comparison()
        while self._match(TokenType.EQ, TokenType.NOT_EQ):
            op = self._previous().value
            right = self._comparison()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _comparison(self) -> ASTNode:
        """Парсим операторы сравнения: <, <=, >, >="""
        expr = self._bitwise_or()
        while self._match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op = self._previous().value
            right = self._bitwise_or()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _bitwise_or(self) -> ASTNode:
        """Парсим побитовое ИЛИ: left | right"""
        expr = self._bitwise_xor()
        while self._match(TokenType.OR):
            op = self._previous().value
            right = self._bitwise_xor()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _bitwise_xor(self) -> ASTNode:
        """Парсим побитовое исключающее ИЛИ: left ^ right"""
        expr = self._bitwise_and()
        while self._match(TokenType.CARET):
            op = self._previous().value
            right = self._bitwise_and()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _bitwise_and(self) -> ASTNode:
        """Парсим побитовое И: left & right"""
        expr = self._shift()
        while self._match(TokenType.AMPERSAND):
            op = self._previous().value
            right = self._shift()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _shift(self) -> ASTNode:
        """Парсим битовые сдвиги: <<, >>"""
        expr = self._addition()
        while self._match(TokenType.SHIFT_LEFT, TokenType.SHIFT_RIGHT):
            op = self._previous().value
            right = self._addition()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _addition(self) -> ASTNode:
        """Парсим сложение и вычитание: +, -"""
        expr = self._multiplication()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            right = self._multiplication()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _multiplication(self) -> ASTNode:
        """Парсим умножение, деление, остаток: *, /, %"""
        expr = self._unary()
        while self._match(TokenType.ASTERISK, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous().value
            right = self._unary()
            expr = BinaryOp(expr, op, right, self._previous().line, self._previous().column)
        return expr

    def _unary(self) -> ASTNode:
        """Парсим унарные операторы: !, -, &, *, <-"""
        if self._match(TokenType.BANG, TokenType.MINUS, TokenType.AMPERSAND, TokenType.ASTERISK):
            op = self._previous().value
            operand = self._unary()
            return UnaryOp(op, operand, self._previous().line, self._previous().column)
        elif self._match(TokenType.ARROW):
            operand = self._unary()
            return UnaryOp("<-", operand, self._previous().line, self._previous().column)
        return self._postfix()

    def _postfix(self) -> ASTNode:
        """Парсим постфиксные операторы: вызовы функций, доступ к членам, операции с каналами"""
        expr = self._primary()
    
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                member_token = self._consume(TokenType.IDENT, "Expected member name after '.'")
                expr = MemberAccess(expr, member_token.value, member_token.line, member_token.column)
            elif self._match(TokenType.ARROW):
                value = self._expression()
                expr = ChannelOperation(expr, value, self._previous().line, self._previous().column)
            elif self._match(TokenType.LEFT_BRACKET):
                expr = self._finish_slice_or_index(expr)

            else:
                break
    
        return expr

    def _finish_call(self, callee: ASTNode) -> CallExpression:
        """Завершаем парсинг вызова функции: callee(args)"""
        args = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                args.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break
        paren = self._consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments")
        return CallExpression(callee, args, paren.line, paren.column)

    def _finish_slice_or_index(self, array: ASTNode) -> BinaryOp:
        """Завершаем парсинг операции индексации: arr[i]"""
        line = self._previous().line
        col = self._previous().column
        
        index = self._expression()
        
        self._consume(TokenType.RIGHT_BRACKET, "Expected ']'")
        return BinaryOp(array, "[", index, line, col)

    def _primary(self) -> ASTNode:
        """Парсим первичные выражения: литералы, идентификаторы, скобки, составные литералы"""
        if self._match(TokenType.TRUE):
            return Literal(True, self._previous().line, self._previous().column)
        if self._match(TokenType.FALSE):
            return Literal(False, self._previous().line, self._previous().column)
        
        if self._match(TokenType.NIL):
            return Literal(None, self._previous().line, self._previous().column)
        
        if self._match(TokenType.INT):
            value = self._previous().value
            return Literal(int(value), self._previous().line, self._previous().column)
        if self._match(TokenType.FLOAT):
            value = self._previous().value
            return Literal(float(value), self._previous().line, self._previous().column)
        
        if self._match(TokenType.STRING):
            value = self._previous().value.strip('"')
            return Literal(value, self._previous().line, self._previous().column)
        
        if self._match(TokenType.IDENT):
            ident = Identifier(self._previous().value, self._previous().line, self._previous().column)
            
            if self._check(TokenType.LEFT_BRACE):
                return self._composite_literal(ident)
            
            return ident
        
        if self._check(TokenType.CHAN):
            return self._parse_type()

        # Скобки
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        raise ParseError(f"Unexpected token in primary expression: {self._peek().type}", self._peek())

    def _composite_literal(self, type_expr: BaseType) -> CompositeLiteral:
        """Парсим составной литерал: T{fields}"""
        line = self._previous().line
        col = self._previous().column
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after type in composite literal")
        
        elements = []
        if not self._check(TokenType.RIGHT_BRACE):
            while True:
                if self._check(TokenType.IDENT) and self._peek_ahead().type == TokenType.COLON:
                    key_token = self._advance()
                    self._consume(TokenType.COLON, "Expected ':' after key in composite literal")
                    value = self._expression()
                    elements.append(KeyValueExpr(Identifier(key_token.value, key_token.line, key_token.column), value, key_token.line, key_token.column))
                else:
                    value = self._expression()
                    elements.append(value)
                
                if not self._match(TokenType.COMMA):
                    break
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after composite literal elements")
        return CompositeLiteral(type_expr, elements, line, col)



    def _is_at_end(self) -> bool:
        """Проверяем, достигли ли конца токенов"""
        return self.current >= len(self.tokens) or self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """Получаем текущий токен без продвижения"""
        if self.current >= len(self.tokens):
            return Token(TokenType.EOF, "", -1, -1)
        return self.tokens[self.current]

    def _peek_ahead(self, offset: int = 1) -> Token:
        """Получаем токен на указанное смещение вперед"""
        pos = self.current + offset
        if pos >= len(self.tokens):
            return Token(TokenType.EOF, "", -1, -1)
        return self.tokens[pos]

    def _previous(self) -> Token:
        """Получаем предыдущий токен"""
        if self.current == 0:
            return Token(TokenType.EOF, "", -1, -1)
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        """Продвигаемся к следующему токену"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()


    def _check(self, *token_types) -> bool:
        """Проверяем тип текущего токена (может принимать несколько типов)"""
        if self._is_at_end():
            return False
        current_token = self._peek()
        return current_token.type in token_types

    def _match(self, *token_types) -> bool:
        """Проверяем и продвигаемся, если текущий токен совпадает с одним из указанных типов"""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Проверяем тип текущего токена и продвигаемся, или выдаем ошибку"""
        if self._check(token_type):
            return self._advance()
        raise ParseError(message, self._peek())