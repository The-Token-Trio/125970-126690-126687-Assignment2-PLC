from __future__ import annotations

from typing import Optional

from components.tokens import Token, TokenType
from components.ast_nodes import (
    ASTNode,
    Program,
    Block,
    Assign,
    If,
    While,
    FunctionDef,
    FunctionCall,
    Print,
    Return,
    BinaryOp,
    Literal,
    Identifier,
)


# ---------------------------------------------------------------------------
# Parser error
# ---------------------------------------------------------------------------

class ParseError(Exception):
    pass


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """Recursive-descent parser.

    Usage:
        tokens = Lexer(source).tokenize()
        tree   = Parser(tokens).parse()   # returns Program node
    """

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -----------------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------------

    def parse(self) -> Program:
        """Parse the full token stream and return the root Program node."""
        line, col = self._peek().line, self._peek().column
        statements: list[ASTNode] = []
        while not self._is_at_end():
            statements.append(self._statement())
        return Program(statements=statements, line=line, column=col)

    # -----------------------------------------------------------------------
    # Statements
    # -----------------------------------------------------------------------

    def _statement(self) -> ASTNode:
        """Dispatch to the correct statement parser based on the current token."""
        tok = self._peek()

        if tok.token_type == TokenType.DEF:
            return self._func_def()

        if tok.token_type == TokenType.IF:
            return self._if_stmt()

        if tok.token_type == TokenType.WHILE:
            return self._while_stmt()

        if tok.token_type == TokenType.RETURN:
            return self._return_stmt()

        if tok.token_type == TokenType.PRINT:
            return self._print_stmt()

        # assignment: IDENTIFIER "=" expr ";"
        if (
            tok.token_type == TokenType.IDENTIFIER
            and self._peek_next().token_type == TokenType.ASSIGN
        ):
            return self._assignment()

        # fallback: bare expression statement  expr ";"
        node = self._expr()
        self._expect(TokenType.SEMICOLON, "Expected ';' after expression")
        return node

    def _assignment(self) -> Assign:
        """IDENTIFIER '=' expr ';'"""
        name_tok = self._advance()                              # IDENTIFIER
        self._advance()                                         # '='
        value = self._expr()
        self._expect(TokenType.SEMICOLON, "Expected ';' after assignment")
        return Assign(name=name_tok.lexeme, value=value,
                      line=name_tok.line, column=name_tok.column)

    def _if_stmt(self) -> If:
        """'if' '(' bool_expr ')' block ( 'else' block )?"""
        tok = self._advance()                                   # 'if'
        self._expect(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self._bool_expr()
        self._expect(TokenType.RPAREN, "Expected ')' after if condition")
        then_block = self._block()
        else_block: Optional[Block] = None
        if self._check(TokenType.ELSE):
            self._advance()                                     # 'else'
            else_block = self._block()
        return If(condition=condition, then_block=then_block, else_block=else_block,
                  line=tok.line, column=tok.column)

    def _while_stmt(self) -> While:
        """'while' '(' bool_expr ')' block"""
        tok = self._advance()                                   # 'while'
        self._expect(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self._bool_expr()
        self._expect(TokenType.RPAREN, "Expected ')' after while condition")
        body = self._block()
        return While(condition=condition, body=body,
                     line=tok.line, column=tok.column)

    def _func_def(self) -> FunctionDef:
        """'def' IDENTIFIER '(' params? ')' block"""
        tok = self._advance()                                   # 'def'
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected function name after 'def'")
        self._expect(TokenType.LPAREN, "Expected '(' after function name")
        params = self._params()
        self._expect(TokenType.RPAREN, "Expected ')' after parameters")
        body = self._block()
        return FunctionDef(name=name_tok.lexeme, params=params, body=body,
                           line=tok.line, column=tok.column)

    def _print_stmt(self) -> Print:
        """'print' '(' expr ')' ';'"""
        tok = self._advance()                                   # 'print'
        self._expect(TokenType.LPAREN, "Expected '(' after 'print'")
        expr = self._expr()
        self._expect(TokenType.RPAREN, "Expected ')' after print expression")
        self._expect(TokenType.SEMICOLON, "Expected ';' after print statement")
        return Print(expr=expr, line=tok.line, column=tok.column)

    def _return_stmt(self) -> Return:
        """'return' expr ';'"""
        tok = self._advance()                                   # 'return'
        expr = self._expr()
        self._expect(TokenType.SEMICOLON, "Expected ';' after return value")
        return Return(expr=expr, line=tok.line, column=tok.column)

    def _block(self) -> Block:
        """'{' statement* '}'"""
        tok = self._expect(TokenType.LBRACE, "Expected '{'")
        statements: list[ASTNode] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            statements.append(self._statement())
        self._expect(TokenType.RBRACE, "Expected '}' to close block")
        return Block(statements=statements, line=tok.line, column=tok.column)

    # -----------------------------------------------------------------------
    # Parameters (function definition)
    # -----------------------------------------------------------------------

    def _params(self) -> list[str]:
        """IDENTIFIER (',' IDENTIFIER)*  — returns list of param names."""
        params: list[str] = []
        if self._check(TokenType.IDENTIFIER):
            params.append(self._advance().lexeme)
            while self._check(TokenType.COMMA):
                self._advance()                                 # ','
                tok = self._expect(TokenType.IDENTIFIER, "Expected parameter name after ','")
                params.append(tok.lexeme)
        return params

    # -----------------------------------------------------------------------
    # Boolean expressions  (lowest precedence, used in if/while conditions)
    # -----------------------------------------------------------------------

    def _bool_expr(self) -> ASTNode:
        """expr ('==' | '!=') expr   |   BOOL_LITERAL"""
        # bare boolean literal: true / false
        if self._check(TokenType.BOOL_LITERAL):
            tok = self._advance()
            value = tok.lexeme == "true"
            return Literal(value=value, line=tok.line, column=tok.column)

        left = self._expr()

        if self._check(TokenType.EQUAL_EQUAL):
            op_tok = self._advance()
            right = self._expr()
            return BinaryOp(op="==", left=left, right=right,
                            line=op_tok.line, column=op_tok.column)

        if self._check(TokenType.BANG_EQUAL):
            op_tok = self._advance()
            right = self._expr()
            return BinaryOp(op="!=", left=left, right=right,
                            line=op_tok.line, column=op_tok.column)

        # no comparison operator found — return the expr as-is
        # (the type checker will validate it's Boolean)
        return left

    # -----------------------------------------------------------------------
    # Arithmetic expressions  (standard precedence)
    # -----------------------------------------------------------------------

    def _expr(self) -> ASTNode:
        """term (('+' | '-') term)*"""
        node = self._term()
        while self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            op_tok = self._advance()
            right = self._term()
            node = BinaryOp(op=op_tok.lexeme, left=node, right=right,
                            line=op_tok.line, column=op_tok.column)
        return node

    def _term(self) -> ASTNode:
        """factor (('*' | '/') factor)*"""
        node = self._factor()
        while self._check(TokenType.STAR) or self._check(TokenType.SLASH):
            op_tok = self._advance()
            right = self._factor()
            node = BinaryOp(op=op_tok.lexeme, left=node, right=right,
                            line=op_tok.line, column=op_tok.column)
        return node

    def _factor(self) -> ASTNode:
        """
        INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL | BOOL_LITERAL
        | IDENTIFIER ( '(' args? ')' )?
        | '(' expr ')'
        """
        tok = self._peek()

        # Integer literal
        if tok.token_type == TokenType.INT_LITERAL:
            self._advance()
            return Literal(value=int(tok.lexeme), line=tok.line, column=tok.column)

        # Float literal
        if tok.token_type == TokenType.FLOAT_LITERAL:
            self._advance()
            return Literal(value=float(tok.lexeme), line=tok.line, column=tok.column)

        # Boolean literal
        if tok.token_type == TokenType.BOOL_LITERAL:
            self._advance()
            return Literal(value=(tok.lexeme == "true"), line=tok.line, column=tok.column)

        # String literal  (keep the surrounding quotes stripped)
        if tok.token_type == TokenType.STRING_LITERAL:
            self._advance()
            return Literal(value=tok.lexeme[1:-1], line=tok.line, column=tok.column)

        # Identifier — could be a plain variable or a function call
        if tok.token_type == TokenType.IDENTIFIER:
            self._advance()
            if self._check(TokenType.LPAREN):
                # function call
                self._advance()                                 # '('
                args = self._args()
                self._expect(TokenType.RPAREN, "Expected ')' after function arguments")
                return FunctionCall(name=tok.lexeme, args=args,
                                    line=tok.line, column=tok.column)
            return Identifier(name=tok.lexeme, line=tok.line, column=tok.column)

        # Grouped expression  '(' expr ')'
        if tok.token_type == TokenType.LPAREN:
            self._advance()                                     # '('
            node = self._expr()
            self._expect(TokenType.RPAREN, "Expected ')' to close grouped expression")
            return node

        raise ParseError(self._error_at(tok, f"Unexpected token: {tok.lexeme!r}"))

    # -----------------------------------------------------------------------
    # Arguments (function call)
    # -----------------------------------------------------------------------

    def _args(self) -> list[ASTNode]:
        """expr (',' expr)*"""
        args: list[ASTNode] = []
        if not self._check(TokenType.RPAREN):
            args.append(self._expr())
            while self._check(TokenType.COMMA):
                self._advance()                                 # ','
                args.append(self._expr())
        return args

    # -----------------------------------------------------------------------
    # Token navigation helpers
    # -----------------------------------------------------------------------

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _peek_next(self) -> Token:
        if self._pos + 1 < len(self._tokens):
            return self._tokens[self._pos + 1]
        return self._tokens[-1]                                 # EOF

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        if not self._is_at_end():
            self._pos += 1
        return tok

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().token_type == token_type

    def _is_at_end(self) -> bool:
        return self._peek().token_type == TokenType.EOF

    def _expect(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise ParseError(self._error_at(self._peek(), message))

    def _error_at(self, tok: Token, message: str) -> str:
        return f"[line {tok.line}, col {tok.column}] ParseError: {message}"