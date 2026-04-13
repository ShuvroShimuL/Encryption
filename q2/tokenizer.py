"""Tokenizer for Q2 — pure function, no I/O, no prints."""

from errors import ParseError


def tokenize(expr: str) -> list:
    """Tokenize an arithmetic expression string into a list of token dicts.

    Token types: NUM, OP, LPAREN, RPAREN, END.
    '-' is always tokenized as OP, never folded into a NUM token.
    Always appends an END token as the final element.

    Raises ParseError on unknown characters or malformed numbers.
    """
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        # Skip whitespace
        if ch in (' ', '\t'):
            i += 1
            continue

        # Number: collect digits and at most one decimal point
        if ch.isdigit() or (ch == '.' and i + 1 < n and expr[i + 1].isdigit()):
            j = i
            seen_dot = False
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if seen_dot:
                        raise ParseError(
                            f"Invalid number format: multiple dots near position {j}"
                        )
                    seen_dot = True
                j += 1
            num_str = expr[i:j]
            tokens.append({"type": "NUM", "value": float(num_str)})
            i = j
            continue

        # Operators
        if ch in ('+', '-', '*', '/'):
            tokens.append({"type": "OP", "value": ch})
            i += 1
            continue

        # Parentheses
        if ch == '(':
            tokens.append({"type": "LPAREN", "value": "("})
            i += 1
            continue

        if ch == ')':
            tokens.append({"type": "RPAREN", "value": ")"})
            i += 1
            continue

        # Unknown character
        raise ParseError(f"Unknown character: {ch!r}")

    tokens.append({"type": "END", "value": None})
    return tokens
