#!/usr/bin/env python3
"""
Format S-expressions for easier debugging.

Usage:
    python3 sexpfmt.py input.sexp
    cat input.sexp | python3 sexpfmt.py
"""

import argparse
import sys
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Token:
    kind: str
    text: str


Sexp = Token | list["Sexp"]


def tokenize(src: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(src)

    while i < n:
        ch = src[i]

        if ch.isspace():
            i += 1
            continue

        if ch in "()":
            tokens.append(Token(ch, ch))
            i += 1
            continue

        if ch == ";":
            start = i
            while i < n and src[i] != "\n":
                i += 1
            tokens.append(Token("comment", src[start:i]))
            continue

        if ch == '"':
            start = i
            i += 1
            escaped = False

            while i < n:
                c = src[i]

                if escaped:
                    escaped = False
                    i += 1
                    continue

                if c == "\\":
                    escaped = True
                    i += 1
                    continue

                if c == '"':
                    i += 1
                    break

                i += 1

            tokens.append(Token("atom", src[start:i]))
            continue

        start = i
        while i < n:
            c = src[i]
            if c.isspace() or c in "();" :
                break
            i += 1

        tokens.append(Token("atom", src[start:i]))

    return tokens


def parse_sexps(tokens: Iterable[Token]) -> list[Sexp]:
    stack: list[list[Sexp]] = [[]]

    for tok in tokens:
        if tok.kind == "(":
            child: list[Sexp] = []
            stack[-1].append(child)
            stack.append(child)
        elif tok.kind == ")":
            if len(stack) > 1:
                stack.pop()
        else:
            stack[-1].append(tok)

    return stack[0]


SKIP_LINE = {"block", "proc", "record", "var", "module"}
KEEP_N_IN_LINE = {"proc": 2, "record": 2, "module": 2}

def format_node(node: Sexp, indent_width: int) -> str:
    if isinstance(node, Token):
        return node.text

    if not node:
        return "()"

    head = node[0]
    if isinstance(head, Token) and head.kind == "atom" and head.text in SKIP_LINE:
        try:
            keep = KEEP_N_IN_LINE[head.text]
        except KeyError:
            keep = 1

        if len(node) <= keep:
            keep = 1

        prefix = "(" + " ".join(format_node(child, indent_width) for child in node[:keep])
        children = node[keep:]

        if not children:
            return prefix + ")"

        lines = [prefix]
        for child in children:
            lines.extend(" " * indent_width + line for line in format_node(child, indent_width).splitlines())
        lines[-1] += ")"
        return "\n".join(lines)

    children = [format_node(child, indent_width) for child in node]
    if all("\n" not in child for child in children):
        return "(" + " ".join(children) + ")"

    if "\n" not in children[0]:
        lines = ["(" + children[0]]
        children = children[1:]
    else:
        lines = ["("]

    for child in children:
        lines.extend(" " * indent_width + line for line in child.splitlines())
    lines[-1] += ")"
    return "\n".join(lines)


def format_sexp(tokens: Iterable[Token], indent_width: int = 2) -> str:
    sexps = parse_sexps(tokens)
    out = [format_node(sexp, indent_width) for sexp in sexps]
    return "\n".join(out) + ("\n" if out else "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Format S-expressions for easier compiler debugging."
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Input file. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "-i",
        "--indent",
        type=int,
        default=2,
        help="Number of spaces per indentation level. Default: 2.",
    )

    args = parser.parse_args(argv)

    if args.indent < 0:
        parser.error("--indent must be non-negative")

    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                src = f.read()
        else:
            src = sys.stdin.read()

        tokens = tokenize(src)
        sys.stdout.write(format_sexp(tokens, args.indent))
        return 0

    except OSError as e:
        print(f"sexpfmt: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
