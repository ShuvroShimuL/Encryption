"""Recursive descent parser for Q2 — pure functions, no I/O, no prints.

Grammar (left-associative using while loops):
    expr    -> term (('+' | '-') term)*
    term    -> unary (('*' | '/') unary)*
    unary   -> '-' unary  |  primary
    primary -> NUMBER [implicit_mul]
             | '(' expr ')' [implicit_mul]

    implicit_mul: if next token is LPAREN, consume it and build BIN * node.

AST node schemas:
    {"type": "NUM",  "value": float}
    {"type": "BIN",  "op": str, "left": node, "right": node}
    {"type": "NEG",  "operand": node}

Parser state: {"tokens": list[dict], "pos": int}
"""

from tokenizer import tokenize
from errors import ParseError

DEBUG = False


# ── State helpers ────────────────────────────────────────────────────────────

def peek(state):
    """Return the current token without advancing."""
    return state["tokens"][state["pos"]]


def consume(state, expected_type=None):
    """Return and advance past the current token.

    If expected_type is given, raises ParseError if the type doesn't match.
    """
    token = state["tokens"][state["pos"]]
    if expected_type and token["type"] != expected_type:
        raise ParseError(
            f"Expected {expected_type}, got {token['type']!r} ({token['value']!r})"
        )
    state["pos"] += 1
    return token


# ── Parsing functions ────────────────────────────────────────────────────────

def parse_expr(state):
    """Parse addition and subtraction (lowest precedence, left-associative)."""
    left = parse_term(state)
    while peek(state)["type"] == "OP" and peek(state)["value"] in ('+', '-'):
        op = consume(state)["value"]
        right = parse_term(state)
        left = {"type": "BIN", "op": op, "left": left, "right": right}
    return left


def parse_term(state):
    """Parse multiplication and division (higher precedence, left-associative)."""
    left = parse_unary(state)
    while peek(state)["type"] == "OP" and peek(state)["value"] in ('*', '/'):
        op = consume(state)["value"]
        right = parse_unary(state)
        left = {"type": "BIN", "op": op, "left": left, "right": right}
    return left


def parse_unary(state):
    """Parse unary negation (right-recursive to handle --5)."""
    tok = peek(state)
    if tok["type"] == "OP" and tok["value"] == '-':
        consume(state)
        operand = parse_unary(state)
        return {"type": "NEG", "operand": operand}
    if tok["type"] == "OP" and tok["value"] == '+':
        raise ParseError("Unary + is not supported")
    return parse_primary(state)


def parse_primary(state):
    """Parse a number, parenthesised expression, or implicit multiplication.

    Implicit multiplication: NUMBER '(' expr ')' or ')' '(' ... is handled
    at the call sites (parse_expr/parse_term call parse_unary which falls
    through here), and after a primary is returned we check for a trailing
    LPAREN to inject a BIN * node.
    """
    tok = peek(state)

    if tok["type"] == "NUM":
        consume(state)
        node = {"type": "NUM", "value": tok["value"]}
        # Implicit multiplication: 2(3+4)
        if peek(state)["type"] == "LPAREN":
            node = _parse_implicit_mul(state, node)
        return node

    if tok["type"] == "LPAREN":
        consume(state)  # consume '('
        node = parse_expr(state)
        consume(state, expected_type="RPAREN")  # consume ')'
        # Implicit multiplication: (a+b)(c+d)
        if peek(state)["type"] == "LPAREN":
            node = _parse_implicit_mul(state, node)
        return node

    raise ParseError(f"Unexpected token: {tok['type']!r} ({tok['value']!r})")


def _parse_implicit_mul(state, left_node):
    """Consume '(' expr ')' and wrap left_node in a BIN * node."""
    consume(state)  # consume '('
    right = parse_expr(state)
    consume(state, expected_type="RPAREN")  # consume ')'
    node = {"type": "BIN", "op": "*", "left": left_node, "right": right}
    # Chain: 2(3)(4) → 2*(3)*(4)
    if peek(state)["type"] == "LPAREN":
        node = _parse_implicit_mul(state, node)
    return node


# ── Public entry point ───────────────────────────────────────────────────────

def parse(expr: str):
    """Tokenize and parse expr, returning (tree_node, tokens_list).

    Raises ParseError on any syntax error.
    """
    tokens = tokenize(expr)
    state = {"tokens": tokens, "pos": 0}

    if DEBUG:
        print(f"[DEBUG] tokens: {tokens}")

    tree = parse_expr(state)

    if peek(state)["type"] != "END":
        raise ParseError(
            f"Unexpected trailing tokens: {peek(state)['value']!r}"
        )

    if DEBUG:
        print(f"[DEBUG] tree: {tree}")

    return tree, tokens
