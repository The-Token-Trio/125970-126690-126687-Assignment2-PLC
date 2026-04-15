from __future__ import annotations

from typing import Iterator

from components.tokens import Token, TokenType


KEYWORDS: dict[str, TokenType] = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT,
    "true": TokenType.BOOL_LITERAL,
    "false": TokenType.BOOL_LITERAL,
}


SINGLE_CHAR_TOKENS: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "=": TokenType.ASSIGN,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ",": TokenType.COMMA,
    ";": TokenType.SEMICOLON,
}


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.token_column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._is_at_end():
            self.start = self.current
            self.token_column = self.column
            token = self._scan_token()
            if token is not None:
                tokens.append(token)
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def _scan_token(self) -> Token | None:
        char = self._advance()

        # Whitespace handling
        if char in {" ", "\t", "\r"}:
            return None
        if char == "\n":
            self.line += 1
            self.column = 1
            return None

        # Two-char operators
        if char == "=":
            if self._match("="):
                return self._make_token(TokenType.EQUAL_EQUAL)
            return self._make_token(TokenType.ASSIGN)
        if char == "!":
            if self._match("="):
                return self._make_token(TokenType.BANG_EQUAL)
            raise LexerError(self._error_message("Unexpected '!'. Did you mean '!='?"))

        # Single-char operators/delimiters
        single_char_token = SINGLE_CHAR_TOKENS.get(char)
        if single_char_token is not None:
            return self._make_token(single_char_token)

        if char == '"':
            return self._string()

        if char.isdigit():
            return self._number()

        if self._is_identifier_start(char):
            return self._identifier()

        raise LexerError(self._error_message(f"Unexpected character: {char!r}"))

    def _string(self) -> Token:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
                self.column = 1
            self._advance()

        if self._is_at_end():
            raise LexerError(self._error_message("Unterminated string literal"))

        # Closing quote
        self._advance()
        return self._make_token(TokenType.STRING_LITERAL)

    def _number(self) -> Token:
        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        if is_float:
            return self._make_token(TokenType.FLOAT_LITERAL)
        return self._make_token(TokenType.INT_LITERAL)

    def _identifier(self) -> Token:
        while self._is_identifier_part(self._peek()):
            self._advance()

        lexeme = self._current_lexeme()
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return self._make_token(token_type)

    def _current_lexeme(self) -> str:
        return self.source[self.start : self.current]

    def _make_token(self, token_type: TokenType) -> Token:
        return Token(token_type, self._current_lexeme(), self.line, self.token_column)

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        self.column += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char.isalpha() or char == "_"

    @staticmethod
    def _is_identifier_part(char: str) -> bool:
        return char.isalnum() or char == "_"

    def _error_message(self, message: str) -> str:
        return f"[line {self.line}, col {self.token_column}] {message}"


def iter_tokens(source: str) -> Iterator[Token]:
    yield from Lexer(source).tokenize()

