"""Tokenizer for the JR-100 DSL."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional


class TokenKind(Enum):
    IDENT = auto()
    DIRECTIVE = auto()
    NUMBER = auto()
    STRING = auto()
    CHAR = auto()
    COMMA = auto()
    COLON = auto()
    HASH = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    AMP = auto()
    PIPE = auto()
    CARET = auto()
    TILDE = auto()
    LSHIFT = auto()
    RSHIFT = auto()
    LPAREN = auto()
    RPAREN = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    value: Optional[str]
    line: int
    column: int


class LexerError(RuntimeError):
    pass


class Lexer:
    def __init__(self, source: str, filename: str = "<stdin>") -> None:
        self.source = source
        self.filename = filename
        self._index = 0
        self._line = 1
        self._column = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            token = self._next_token()
            tokens.append(token)
            if token.kind == TokenKind.EOF:
                break
        return tokens

    def _next_token(self) -> Token:
        self._skip_whitespace()
        if self._index >= len(self.source):
            return Token(TokenKind.EOF, None, self._line, self._column)

        ch = self.source[self._index]
        if ch == '\n':
            token = Token(TokenKind.NEWLINE, None, self._line, self._column)
            self._advance()
            return token
        if ch == ',':
            token = Token(TokenKind.COMMA, None, self._line, self._column)
            self._advance()
            return token
        if ch == ':':
            token = Token(TokenKind.COLON, None, self._line, self._column)
            self._advance()
            return token
        if ch == '#':
            token = Token(TokenKind.HASH, None, self._line, self._column)
            self._advance()
            return token
        if ch == '+':
            token = Token(TokenKind.PLUS, None, self._line, self._column)
            self._advance()
            return token
        if ch == '-':
            token = Token(TokenKind.MINUS, None, self._line, self._column)
            self._advance()
            return token
        if ch == '*':
            token = Token(TokenKind.STAR, None, self._line, self._column)
            self._advance()
            return token
        if ch == '/':
            token = Token(TokenKind.SLASH, None, self._line, self._column)
            self._advance()
            return token
        if ch == '&':
            token = Token(TokenKind.AMP, None, self._line, self._column)
            self._advance()
            return token
        if ch == '|':
            token = Token(TokenKind.PIPE, None, self._line, self._column)
            self._advance()
            return token
        if ch == '^':
            token = Token(TokenKind.CARET, None, self._line, self._column)
            self._advance()
            return token
        if ch == '~':
            token = Token(TokenKind.TILDE, None, self._line, self._column)
            self._advance()
            return token
        if ch == '(':
            token = Token(TokenKind.LPAREN, None, self._line, self._column)
            self._advance()
            return token
        if ch == ')':
            token = Token(TokenKind.RPAREN, None, self._line, self._column)
            self._advance()
            return token
        if ch == '<' and self._peek() == '<':
            token = Token(TokenKind.LSHIFT, None, self._line, self._column)
            self._advance(2)
            return token
        if ch == '>' and self._peek() == '>':
            token = Token(TokenKind.RSHIFT, None, self._line, self._column)
            self._advance(2)
            return token
        if ch == '"':
            return self._lex_string()
        if ch == '\'':
            return self._lex_char()
        if ch.isdigit() or ch in '$%':
            return self._lex_number()
        if ch == '.':
            return self._lex_directive()
        if ch.isalpha() or ch == '_':
            return self._lex_identifier()

        raise LexerError(f"Unexpected character {ch!r} at {self.filename}:{self._line}:{self._column}")

    def _skip_whitespace(self) -> None:
        while self._index < len(self.source):
            ch = self.source[self._index]
            if ch in ' \t\r':
                self._advance()
                continue
            if ch == ';':
                self._consume_comment()
                continue
            break

    def _consume_comment(self) -> None:
        while self._index < len(self.source) and self.source[self._index] != '\n':
            self._advance()

    def _lex_identifier(self) -> Token:
        start = self._index
        while self._index < len(self.source) and (self.source[self._index].isalnum() or self.source[self._index] == '_'):
            self._advance()
        value = self.source[start:self._index]
        return Token(TokenKind.IDENT, value.upper(), self._line, self._column - (self._index - start))

    def _lex_directive(self) -> Token:
        start = self._index
        self._advance()
        while self._index < len(self.source) and self.source[self._index].isalpha():
            self._advance()
        value = self.source[start:self._index]
        return Token(TokenKind.DIRECTIVE, value.lower(), self._line, self._column - (self._index - start))

    def _lex_number(self) -> Token:
        start = self._index
        prefix = self.source[self._index]
        if prefix == '$':
            self._advance()
            while self._index < len(self.source) and self.source[self._index].isalnum():
                self._advance()
        elif prefix == '%':
            self._advance()
            while self._index < len(self.source) and self.source[self._index] in '01':
                self._advance()
        else:
            while self._index < len(self.source) and self.source[self._index].isdigit():
                self._advance()
        value = self.source[start:self._index]
        return Token(TokenKind.NUMBER, value, self._line, self._column - (self._index - start))

    def _lex_string(self) -> Token:
        line = self._line
        column = self._column
        self._advance()  # opening quote
        chars: List[str] = []
        while self._index < len(self.source):
            ch = self.source[self._index]
            if ch == '"':
                self._advance()
                break
            if ch == '\\':
                self._advance()
                if self._index >= len(self.source):
                    raise LexerError(f"Unterminated escape sequence at {self.filename}:{line}:{column}")
                escape = self.source[self._index]
                self._advance()
                chars.append(f"\\{escape}")
                continue
            chars.append(ch)
            self._advance()
        else:
            raise LexerError(f"Unterminated string at {self.filename}:{line}:{column}")
        value = '"' + ''.join(chars) + '"'
        return Token(TokenKind.STRING, value, line, column)

    def _lex_char(self) -> Token:
        line = self._line
        column = self._column
        self._advance()  # opening quote
        if self._index >= len(self.source):
            raise LexerError(f"Unterminated char literal at {self.filename}:{line}:{column}")
        ch = self.source[self._index]
        if ch == '\\':
            self._advance()
            if self._index >= len(self.source):
                raise LexerError(f"Unterminated escape sequence at {self.filename}:{line}:{column}")
            escape = self.source[self._index]
            self._advance()
            literal = f"\\{escape}"
        else:
            self._advance()
            literal = ch
        if self._index >= len(self.source) or self.source[self._index] != '\'':
            raise LexerError(f"Unterminated char literal at {self.filename}:{line}:{column}")
        self._advance()  # closing quote
        return Token(TokenKind.CHAR, literal, line, column)

    def _peek(self) -> Optional[str]:
        if self._index + 1 >= len(self.source):
            return None
        return self.source[self._index + 1]

    def _advance(self, count: int = 1) -> None:
        for _ in range(count):
            if self._index >= len(self.source):
                return
            if self.source[self._index] == '\n':
                self._line += 1
                self._column = 1
            else:
                self._column += 1
            self._index += 1
