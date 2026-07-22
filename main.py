from __future__ import annotations
from dataclasses import dataclass
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
    Caret = "^"

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

    Eq = "="
    NotEq = "!="
    Gt = ">"
    Lt = "<"
    GtEq = ">="
    LtEq = "<="

    LogicAnd = "and"
    LogicOr = "or"
    LogicNot = "not"

    Var = "var"
    Const = "const"
    Module = "module"
    Begin = "begin"
    End = "end"
    Func = "func"
    If = "if"
    Elif = "elif"
    Else = "else"
    Then = "then"
    While = "while"

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
    value: None | int | float | str | Identifier
    kind: TokenKind


INTEGER_PATTERN = re.compile(r"[0-9_]+")

IDENTIFER_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")

WHITESPACE_PATTERN = re.compile(r"\s+")

# TODO: proper function to scan and handle escape sequences n shit
STRING_PATTERN = re.compile(r'".*?"')

SEPARATORS = {
    TokenKind.ParenOpen,
    TokenKind.ParenClose,
    TokenKind.SquareOpen,
    TokenKind.SquareClose,
    TokenKind.CurlyOpen,
    TokenKind.CurlyClose,
    TokenKind.Caret,
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
    TokenKind.Assign,
    TokenKind.Eq,
    TokenKind.NotEq,
    TokenKind.Gt,
    TokenKind.Lt,
    TokenKind.GtEq,
    TokenKind.LtEq,
}

SEPARATOR_SCAN_ORDER: list[str] = list(map(lambda op: op.value, SEPARATORS))
SEPARATOR_SCAN_ORDER.sort(reverse=True)

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

    # Comparison
    TokenKind.Eq,
    TokenKind.NotEq,
    TokenKind.Gt,
    TokenKind.Lt,
    TokenKind.GtEq,
    TokenKind.LtEq,
}

KEYWORDS = [
    TokenKind.LogicAnd,
    TokenKind.LogicOr,
    TokenKind.LogicNot,
    TokenKind.Var,
    TokenKind.Const,
    TokenKind.Module,
    TokenKind.Begin,
    TokenKind.End,
    TokenKind.Func,
    TokenKind.If,
    TokenKind.Elif,
    TokenKind.Else,
    TokenKind.Then,
    TokenKind.While,
]
KEYWORDS = list(map(lambda k: k.value, KEYWORDS))
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

    def scan_separator(self) -> Token:
        x = self.source[self.current : min(len(self.source), self.current + 2)]
        for op in SEPARATOR_SCAN_ORDER:
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
            return self.scan_separator()

    def peek_token(self) -> Token:
        current = self.current
        res = self.next_token()
        self.current = current
        return res


class Identifier(str):
    pass


@dataclass
class File:
    module_name: Identifier
    top_level: list[Node]


type Type = Pointer | Array | Slice | Identifier


@dataclass
class Pointer:
    inner: Type

    def __str__(self) -> str:
        return f"(pointer {self.inner})"


@dataclass
class Array:
    size: int
    inner: Type

    def __str__(self) -> str:
        return f"(array {self.size} {self.inner})"


@dataclass
class Slice:
    inner: Type

    def __str__(self) -> str:
        return f"(slice {self.inner})"


@dataclass
class Node:
    value: int | float | str | Identifier | Binary | Unary | Call | File | Type | VarBlock | ConstBlock
    parent: Node | None = None

    def __str__(self) -> str:
        return _format_node(self)


@dataclass
class IdDecl:
    sym: Identifier
    typ: Type
    value: Node | None = None

@dataclass
class VarBlock:
    declarations: list[IdDecl]

@dataclass
class ConstBlock:
    declarations: list[IdDecl]

def _format_node(node: Node) -> str:
    v = node.value
    if isinstance(v, Unary):
        return f"({v.operator.value} {_format_node(v.operand)})"
    elif isinstance(v, Binary):
        return f"({v.operator.value} {_format_node(v.left)} {_format_node(v.right)})"
    elif isinstance(v, Call):
        args = " ".join(map(_format_node, v.args))
        return f"(call {_format_node(v.callable)} {args})"
    elif isinstance(v, Identifier):
        return f"{v}"
    elif isinstance(v, int):
        return str(v)
    elif isinstance(v, str):
        return v
    elif isinstance(v, File):
        res = [f"(module {v.module_name}"]
        for stmt in v.top_level:
            res.append(_format_node(stmt))
        return " ".join(res) + ")"
    elif isinstance(v, VarBlock):
        res = [f"(var"]
        for decl in v.declarations:
            if decl.value is not None:
                res.append(f"({decl.sym} {decl.typ} {_format_node(decl.value)})")
            else:
                res.append(f"({decl.sym} {decl.typ})")
        return " ".join(res) + ")"
    elif isinstance(v, ConstBlock):
        res = [f"(const"]
        for decl in v.declarations:
            if decl.value is not None:
                res.append(f"({decl.sym} {decl.typ} {_format_node(decl.value)})")
            else:
                res.append(f"({decl.sym} {decl.typ})")
        return " ".join(res) + ")"
    else:
        raise TypeError(f"invalid node type {type(node)}")

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

    def next_matching(self, desired: TokenKind) -> Token | None:
        tok = self.lexer.peek_token()
        if tok.kind != desired:
            return None
        _ = self.lexer.next_token()
        return tok

    def expect(self, target: TokenKind) -> Token:
        tk = self.lexer.next_token()
        if tk.kind != target:
            raise ValueError(f"expected {target} found {tk.kind}")
        return tk

    def parse(self) -> Node:
        return self._parse_file()

    def _parse_file(self) -> Node:
        # Module header is required
        _ = self.expect(TokenKind.Module)
        name = self.expect(TokenKind.Identifier)
        _ = self.expect(TokenKind.Semicolon)
        assert isinstance(name.value, Identifier)

        top_level: list[Node] = []

        while True:
            look = self.peek()
            if look.kind == TokenKind.EndOfFile: break

            if look.kind == TokenKind.Var:
                top_level.append(self._parse_var_block())
            elif look.kind == TokenKind.Const:
                top_level.append(self._parse_const_block())
            else:
                raise NotImplemented("bruh")

        file = Node(value=File(module_name=name.value, top_level=top_level))
        return file

    def _parse_type(self) -> Type:
        name = self.next_matching(TokenKind.Identifier)
        if name is not None:
            assert isinstance(name.value, Identifier)
            return name.value

        if self.next_matching(TokenKind.Caret) is not None:
            return Pointer(inner=self._parse_type())

        if self.next_matching(TokenKind.SquareOpen) is not None:
            # TODO: Support constants and then any compile-time expression
            size = self.next_matching(TokenKind.Integer)

            if size is not None:
                assert isinstance(size.value, int)
                self.expect(TokenKind.SquareClose)
                return Array(size=size.value, inner=self._parse_type())

            elif self.next_matching(TokenKind.SquareClose):
                return Slice(inner=self._parse_type())

        raise ValueError(
            f"expected array, slice, pointer or identifier. found: {self.peek()}"
        )

    def _parse_expr_list(self, end_sep: TokenKind | None) -> list[Node]:
        exprs: list[Node] = []
        while True:
            node = self._parse_expr(0)
            exprs.append(node)

            look = self.peek()
            if look.kind == TokenKind.Comma:
                _ = self.next()

                # Allow trailing comma if next token is the end marker
                delim = self.peek()
                if delim.kind == end_sep:
                    break
                continue
            elif look.kind == end_sep or look.kind == TokenKind.EndOfFile:
                break
            else:
                raise ValueError(f"expected `,` or `{end_sep.value}`, found: {look}")

        if len(exprs) == 0:
            raise ValueError(f"expected at least one expression")

        return exprs

    def _parse_id_list(self, end_sep: TokenKind) -> list[Identifier]:
        ids: list[Identifier] = []

        while True:
            id = self.expect(TokenKind.Identifier)
            assert isinstance(id.value, Identifier)
            ids.append(id.value)

            look = self.peek()
            if look.kind == TokenKind.Comma:
                _ = self.next()

                # Allow trailing comma if next token is the end marker
                delim = self.peek()
                if delim.kind == end_sep:
                    break
                continue
            elif look.kind == end_sep or look.kind == TokenKind.EndOfFile:
                break
            else:
                raise ValueError(f"expected `,` or `{end_sep.value}`, found: {look}")

        return ids

    def _parse_const_block(self) -> Node:
        _ = self.expect(TokenKind.Const)
        decls: list[IdDecl] = []

        while True:
            if self.peek().kind != TokenKind.Identifier:
                break

            ids = self._parse_id_list(TokenKind.Colon)

            _ = self.expect(TokenKind.Colon)
            typ = self._parse_type()

            exprs = []
            if self.next_matching(TokenKind.Assign):
                exprs = self._parse_expr_list(TokenKind.Semicolon)

            _ = self.expect(TokenKind.Semicolon)
            if len(ids) != len(exprs):
                raise ValueError(f"all constant expressions must be associated with a expression")

            for (ident, expr) in zip(ids, exprs):
                decls.append(IdDecl(sym=ident, typ=typ, value=expr))
        
        if len(decls) == 0:
            raise ValueError("empty var declarations are not allowed")
        
        return Node(value=ConstBlock(decls))

    def _parse_var_block(self) -> Node:
        _ = self.expect(TokenKind.Var)
        decls: list[IdDecl] = []

        while True:
            if self.peek().kind != TokenKind.Identifier:
                break

            ids = self._parse_id_list(TokenKind.Colon)

            _ = self.expect(TokenKind.Colon)
            typ = self._parse_type()

            exprs = [None] * len(ids)
            if self.next_matching(TokenKind.Assign):
                exprs = self._parse_expr_list(TokenKind.Semicolon)

            _ = self.expect(TokenKind.Semicolon)
            if len(ids) != len(exprs):
                raise ValueError(f"mismatched number of bindigns for expressions {len(ids)} != {len(exprs)}")

            for (ident, expr) in zip(ids, exprs):
                decls.append(IdDecl(sym=ident, typ=typ, value=expr))
        
        if len(decls) == 0:
            raise ValueError("empty var declarations are not allowed")
        
        return Node(value=VarBlock(decls))

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


def main():
    src = ""
    with open("example.txt", "r") as f:
        src = f.read()

    lex = Lexer(src)
    parser = Parser(lex)
    node = parser.parse()
    print(node)


if __name__ == "__main__":
    main()
