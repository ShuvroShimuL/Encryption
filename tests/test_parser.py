"""Tests for q2/parser.py — plain assert only."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'q2'))
from parser import parse, parse_expr, parse_term, parse_unary, parse_primary
from tokenizer import tokenize
from errors import ParseError


def raises(exc_type, fn, *args, **kwargs):
    """Return True if fn(*args) raises exc_type, else assert-friendly."""
    try:
        fn(*args, **kwargs)
        return False
    except exc_type:
        return True


def make_state(expr):
    """Create a fresh parser state dict from an expression string."""
    return {"tokens": tokenize(expr), "pos": 0}


# ── parse_expr: success cases ────────────────────────────────────────────────

# "3+5" → BIN with op="+"
tree, _ = parse("3+5")
assert tree["type"] == "BIN"
assert tree["op"] == "+"
assert tree["left"]["type"] == "NUM" and tree["left"]["value"] == 3.0
assert tree["right"]["type"] == "NUM" and tree["right"]["value"] == 5.0

# "2 + 3 * 4" → BIN(+, 2, BIN(*, 3, 4)) — precedence: * binds tighter
tree, _ = parse("2 + 3 * 4")
assert tree["type"] == "BIN" and tree["op"] == "+"
assert tree["right"]["type"] == "BIN" and tree["right"]["op"] == "*"

# Left-associativity: "10-5-2" → BIN(-, BIN(-, 10, 5), 2)  not  BIN(-, 10, BIN(-, 5, 2))
tree, _ = parse("10-5-2")
assert tree["type"] == "BIN" and tree["op"] == "-"
assert tree["left"]["type"] == "BIN" and tree["left"]["op"] == "-", \
    "Left-associativity broken: left child should be a BIN, not a NUM"
assert tree["left"]["left"]["value"] == 10.0
assert tree["left"]["right"]["value"] == 5.0
assert tree["right"]["value"] == 2.0

# "3 - 2 + 1" → BIN(+, BIN(-, 3, 2), 1)
tree, _ = parse("3 - 2 + 1")
assert tree["op"] == "+"
assert tree["left"]["op"] == "-"


# ── parse_term: success cases ────────────────────────────────────────────────

# "6 * 2" → BIN with op="*"
tree, _ = parse("6 * 2")
assert tree["type"] == "BIN" and tree["op"] == "*"

# "12 / 3 / 2" → BIN(/, BIN(/, 12, 3), 2) — left-associative
tree, _ = parse("12 / 3 / 2")
assert tree["op"] == "/"
assert tree["left"]["op"] == "/"


# ── parse_unary: success cases ───────────────────────────────────────────────

# "-5" → NEG node
tree, _ = parse("-5")
assert tree["type"] == "NEG"
assert tree["operand"]["type"] == "NUM"
assert tree["operand"]["value"] == 5.0

# "--5" → NEG whose operand is NEG
tree, _ = parse("--5")
assert tree["type"] == "NEG"
assert tree["operand"]["type"] == "NEG"
assert tree["operand"]["operand"]["value"] == 5.0

# "-(3+4)" → NEG of BIN
tree, _ = parse("-(3+4)")
assert tree["type"] == "NEG"
assert tree["operand"]["type"] == "BIN"
assert tree["operand"]["op"] == "+"

# "-3 * 4" → BIN(*, NEG(3), 4)  — unary binds tightest
tree, _ = parse("-3 * 4")
assert tree["type"] == "BIN" and tree["op"] == "*"
assert tree["left"]["type"] == "NEG"


# ── parse_primary: success cases ─────────────────────────────────────────────

# Simple number
tree, _ = parse("42")
assert tree["type"] == "NUM" and tree["value"] == 42.0

# Parenthesised expression
tree, _ = parse("(3 + 4)")
assert tree["type"] == "BIN" and tree["op"] == "+"

# Implicit multiplication: "2(3+4)" → BIN(*, 2, BIN(+,3,4))
tree, _ = parse("2(3+4)")
assert tree["type"] == "BIN" and tree["op"] == "*"
assert tree["left"]["type"] == "NUM" and tree["left"]["value"] == 2.0
assert tree["right"]["type"] == "BIN" and tree["right"]["op"] == "+"

# Implicit multiplication: "(2+1)(3+4)" → BIN(*, BIN(+,2,1), BIN(+,3,4))
tree, _ = parse("(2+1)(3+4)")
assert tree["type"] == "BIN" and tree["op"] == "*"
assert tree["left"]["type"] == "BIN"
assert tree["right"]["type"] == "BIN"


# ── parse_unary: failure cases ───────────────────────────────────────────────

# "+5" → ParseError (unary + not supported)
assert raises(ParseError, parse, "+5"), "Expected ParseError for unary +"
assert raises(ParseError, parse, "+3+4"), "Expected ParseError for leading +"


# ── parse_expr: failure cases ────────────────────────────────────────────────

# "3+" → ParseError (missing right operand)
assert raises(ParseError, parse, "3+"), "Expected ParseError for '3+'"

# "(3+5" → ParseError (unclosed paren → missing RPAREN)
assert raises(ParseError, parse, "(3+5"), "Expected ParseError for '(3+5'"


# ── parse_primary: failure cases ─────────────────────────────────────────────

# Unexpected token at start
assert raises(ParseError, parse, ")5"), "Expected ParseError for ')5'"


# ── Trailing token check ──────────────────────────────────────────────────────

# "3+5 garbage" is impossible (@ raises in tokenizer), but trailing NUM after complete expr fails
assert raises(ParseError, parse, "3+5)"), "Expected ParseError for trailing ')'"


# ── Full sample expressions ───────────────────────────────────────────────────

# Complex: "(10 - 2) * 3 + -4 / 2"
tree, _ = parse("(10 - 2) * 3 + -4 / 2")
assert tree["type"] == "BIN" and tree["op"] == "+"

# Division by zero → parse succeeds (only evaluate fails)
tree, tokens = parse("1 / 0")
assert tree["type"] == "BIN" and tree["op"] == "/"
assert tree["right"]["value"] == 0.0


if __name__ == "__main__":
    print("All parser tests passed.")
