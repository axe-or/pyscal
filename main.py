from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re


class TokenKind(Enum):
    ParenOpen = "("
    ParenClose = ")"
    SquareOpen = "["
    SquareClose = "]"
    CurlyOpen = "{"
    CurlyClose = "}"

    Colon = ":"
    Comma = ","
    Dot = "."
    Semicolon = ";"

    Plus = "+"
    Minus = "-"
    Star = "*"
    Slash = "/"
    Mod = "%"

    And = "&"
    Pipe = "|"
    Tilde = "~"
    ShLeft = "<<"
    ShRight = ">>"

    Eq = "=="
    NotEq = "!="
    Gt = ">"
    Lt = "<"
    GtEq = ">="
    LtEq = "<="

    LogicAnd = "and"
    LogicOr = "or"
    LogicNot = "not"

    If = "if"
    Elif = "elif"
    Else = "else"
    Let = "let"

    Assign = "="

    Identifier = "<id>"
    Integer = "<integer>"
    String = "<string>"

    EndOfFile = "<eof>"

    def is_primary(self) -> bool:
        return self in [TokenKind.Identifier, TokenKind.Integer, TokenKind.String]

    def is_operator(self) -> bool:
        return self in OPERATORS


@dataclass
class Token:
    offset: int
    lexeme: str
    value: None | int | float | str
    kind: TokenKind


INTEGER_PATTERN = re.compile(r"[0-9_]+")

IDENTIFER_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

WHITESPACE_PATTERN = re.compile(r"\s+")

# TODO: proper function to scan and handle escape sequences n shit
STRING_PATTERN = re.compile(r'".*?"')

OPERATORS = {
    # Regular operators
    TokenKind.ParenOpen,
    TokenKind.ParenClose,
    TokenKind.SquareOpen,
    TokenKind.SquareClose,
    TokenKind.CurlyOpen,
    TokenKind.CurlyClose,
    TokenKind.Colon,
    TokenKind.Comma,
    TokenKind.Dot,
    TokenKind.Semicolon,
    TokenKind.Plus,
    TokenKind.Minus,
    TokenKind.Star,
    TokenKind.Slash,
    TokenKind.Mod,
    TokenKind.And,
    TokenKind.Pipe,
    TokenKind.Tilde,
    TokenKind.ShLeft,
    TokenKind.ShRight,
    # Keyword operators
    TokenKind.LogicAnd,
    TokenKind.LogicOr,
    TokenKind.LogicNot,
}

OPERATOR_SCAN_ORDER = list(map(lambda op: op.value, OPERATORS))
OPERATOR_SCAN_ORDER.sort(reverse=True)

KEYWORDS = [
    "and",
    "or",
    "not",
    "if",
    "elif",
    "else",
    "let",
]
KEYWORDS.sort(reverse=True)


@dataclass
class Lexer:
    source: str
    current: int = 0

    def skip_whitespace(self) -> int:
        m = WHITESPACE_PATTERN.match(self.source, pos=self.current)
        if m is None:
            return 0
        start, end = m.span()
        count = end - start
        self.current += count
        return count

    def scan_integer(self) -> Token:
        m = INTEGER_PATTERN.match(self.source, pos=self.current)
        assert m is not None, "not an integer"
        lexeme = m.group()
        val = int(m.group())

        self.current += len(lexeme)
        return Token(
            lexeme=lexeme, value=val, offset=self.current, kind=TokenKind.Integer
        )

    def scan_string(self) -> Token:
        m = STRING_PATTERN.match(self.source, pos=self.current)
        assert m is not None, "not an integer"
        lexeme = m.group()
        val = m.group().strip('"')

        self.current += len(lexeme)
        return Token(
            lexeme=lexeme, value=val, offset=self.current, kind=TokenKind.String
        )

    def scan_identifier_or_keyword(self) -> Token:
        m = IDENTIFER_PATTERN.match(self.source, pos=self.current)
        assert m is not None, "not an identifier"
        lexeme = m.group()
        tok = Token(
            lexeme=lexeme,
            value=Identifier(lexeme),
            offset=self.current,
            kind=TokenKind.Identifier,
        )

        for kw in KEYWORDS:
            if lexeme == kw:
                tok.kind = TokenKind(kw)

        self.current += len(lexeme)
        return tok

    def scan_operator(self) -> Token:
        x = self.source[self.current : min(len(self.source), self.current + 2)]
        for op in OPERATOR_SCAN_ORDER:
            if x.startswith(op):
                self.current += len(op)
                return Token(
                    offset=self.current, lexeme=op, value=None, kind=TokenKind(op)
                )

        raise ValueError(f"not a valid operator: {x}")

    def peek(self, offset: int = 0) -> str | None:
        pos = self.current + offset
        if (pos < 0) or (pos >= len(self.source)):
            return None
        return self.source[pos]

    def next_token(self) -> Token:
        self.skip_whitespace()

        c = self.peek()
        if c is None:
            return Token(
                offset=self.current, lexeme="", kind=TokenKind.EndOfFile, value=None
            )

        if c == '"':
            return self.scan_string()
        elif c.isalpha() or c == "_":
            return self.scan_identifier_or_keyword()
        elif c.isnumeric():
            return self.scan_integer()
        else:
            return self.scan_operator()

    def peek_token(self) -> Token:
        current = self.current
        res = self.next_token()
        self.current = current
        return res


class Identifier(str):
    pass


@dataclass
class Node:
    value: int | float | str | Identifier | Binary | Unary | Call
    parent: Node | None = None


@dataclass
class Binary:
    operator: TokenKind
    left: Node
    right: Node


@dataclass
class Unary:
    operator: TokenKind
    operand: Node


@dataclass
class Call:
    callable: Node
    args: list[Node]


PREFIX_POWER = {
    TokenKind.Plus: 100,
    TokenKind.Minus: 100,
}

INFIX_POWER = {
    TokenKind.SquareOpen: (200, 0),
    TokenKind.ParenOpen: (200, 0),
    TokenKind.Star: (70, 71),
    TokenKind.Slash: (70, 71),
    TokenKind.Mod: (70, 71),
    TokenKind.And: (70, 71),
    TokenKind.ShLeft: (70, 71),
    TokenKind.ShRight: (70, 71),
    TokenKind.Plus: (60, 61),
    TokenKind.Minus: (60, 61),
    TokenKind.Pipe: (60, 61),
    TokenKind.Tilde: (60, 61),
    TokenKind.Eq: (50, 51),
    TokenKind.NotEq: (50, 51),
    TokenKind.Gt: (50, 51),
    TokenKind.GtEq: (50, 51),
    TokenKind.Lt: (50, 51),
    TokenKind.LtEq: (50, 51),
    TokenKind.LogicAnd: (40, 41),
    TokenKind.LogicOr: (30, 31),
}


def infix_binding_power(op: TokenKind) -> tuple[int, int] | None:
    try:
        return INFIX_POWER[op]
    except KeyError:
        return None


def prefix_binding_power(op: TokenKind) -> int | None:
    try:
        return PREFIX_POWER[op]
    except KeyError:
        return None


MIN_BP = -(1 << 31)


@dataclass
class Parser:
    lexer: Lexer

    def peek(self) -> Token:
        return self.lexer.peek_token()

    def next(self) -> Token:
        return self.lexer.next_token()

    def expect(self, target: TokenKind) -> Token:
        tk = self.lexer.next_token()
        if tk.kind != target:
            raise ValueError(f"expected {target} found {tk.kind}")
        return tk

    def _parse_expr(self, min_bp: int) -> Node:
        look = self.peek()
        if look.kind == TokenKind.EndOfFile:
            raise ValueError("unexpected end of file")

        lhs: Node | None = None
        if look.kind.is_primary():
            _ = self.next()
            assert look.value is not None
            lhs = Node(value=look.value)
        elif look.kind == TokenKind.ParenOpen:
            _ = self.next()
            lhs = self._parse_expr(0)
            self.expect(TokenKind.ParenClose)
        elif look.kind.is_operator():
            _ = self.next()
            r_bp = prefix_binding_power(look.kind)
            if r_bp is None:
                raise ValueError(f"not a prefix operator: {look.kind}")

            rhs = self._parse_expr(r_bp)
            lhs = Node(value=Unary(operator=look.kind, operand=rhs))
        else:
            raise ValueError(f"unexpected token: {look.kind}")

        while True:
            op = self.peek()

            l_bp, r_bp = infix_binding_power(op.kind) or (MIN_BP, MIN_BP)
            if l_bp < min_bp:
                break

            _ = self.next()
            if op.kind == TokenKind.SquareOpen:
                raise NotImplementedError("indexing")
            elif op.kind == TokenKind.ParenOpen:
                raise NotImplementedError("call")
            else:
                rhs = self._parse_expr(r_bp)
                lhs = Node(value=Binary(operator=op.kind, left=lhs, right=rhs))

        return lhs


def print_node(node: Node) -> str:
    v = node.value
    if isinstance(v, Unary):
        return f"({v.operator.value} {print_node(v.operand)})"
    elif isinstance(v, Binary):
        return f"({v.operator.value} {print_node(v.left)} {print_node(v.right)})"
    elif isinstance(v, Call):
        args = " ".join(map(print_node, v.args))
        return f"(call {print_node(v.callable)} {args})"
    elif isinstance(v, Identifier):
        return f"{v}"
    elif isinstance(v, int):
        return str(v)
    elif isinstance(v, str):
        return v
    else:
        raise TypeError(f"invalid node type {type(node)}")


def main():
    lex = Lexer("4 + 6 / (8 * 1) and skibidi << 5")

    parser = Parser(lex)
    node = parser._parse_expr(0)

    x = print_node(node)
    print(x)


if __name__ == "__main__":
    main()
