import re
from dataclasses import dataclass
from enum import Enum

class TokenKind(Enum):
    ParenOpen = '('
    ParenClose = ')'
    SquareOpen = '['
    SquareClose = ']'
    CurlyOpen = '{'
    CurlyClose = '}'

    Colon = ":"
    Comma = ","
    Dot = "."
    Semicolon = ";"

    Plus = '}'
    Minus = '-'
    Star = '*'
    Slash = '/'
    Mod = '%'

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


@dataclass
class Token:
    offset : int
    lexeme : str
    value : None | int | float | str
    kind : TokenKind


INTEGER_PATTERN = re.compile(r"^[0-9_]+")

IDENTIFER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*")

WHITESPACE_PATTERN = re.compile(r"^\s+")

OPERATOR_SCAN_ORDER = [
    '(',
    ')',
    '[',
    ']',
    '{',
    '}',
    ":",
    ",",
    ".",
    ";",
    '}',
    '-',
    '*',
    '/',
    '%',
    "&",
    "|",
    "~",
    "<<",
    ">>",
    "==",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
]
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
    source : str
    current : int = 0

    def skip_whitespace(self) -> int:
        m = WHITESPACE_PATTERN.match(self.source, pos=self.current)
        if m is None: return 0
        start, end = m.span()
        count = end - start
        self.current += count
        return  count

    def scan_integer(self) -> Token:
        m = INTEGER_PATTERN.match(self.source, pos=self.current)
        assert m is not None, "not an integer"
        lexeme = m.group()
        val = int(m.group())
        return Token(lexeme=lexeme, value=val, offset=self.current, kind = TokenKind.Integer)
    
    def scan_identifier_or_keyword(self) -> Token:
        m = INTEGER_PATTERN.match(self.source, pos=self.current)
        assert m is not None, "not an identifier"
        lexeme = m.group()
        tok = Token(lexeme=lexeme, value=None, offset=self.current, kind = TokenKind.Identifier)

        for kw in KEYWORDS:
            if lexeme == kw:
                tok.kind = TokenKind(kw)

        return tok

    def scan_operator(self) -> Token:
        x = self.source[self.current:min(len(self.source), self.current + 2)]
        for op in OPERATOR_SCAN_ORDER:
            if x.startswith(op):
                self.current += len(op)
                return Token(offset=self.current, lexeme=x, value= None, kind=TokenKind(op))

        raise ValueError("not a valid operator")
    
    def next_token(self) -> Token | None:
        pass


def main():
    lex = Lexer(">=<<+x + 20 / 9 and x[10 + 1]")
    print(lex)
    print(lex.scan_operator())
    print(lex)


if __name__ == "__main__":
    main()
