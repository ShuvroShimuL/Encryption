"""Tests for q2/evaluator.py — plain assert only."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'q2'))
from evaluator import evaluate, evaluate_file
from formatter import format_result
from parser import parse
from errors import ParseError


def raises(exc_type, fn, *args, **kwargs):
    """Return True if fn(*args) raises exc_type."""
    try:
        fn(*args, **kwargs)
        return False
    except exc_type:
        return True


# ── Byte-for-byte output match ───────────────────────────────────────────────
sample_input = os.path.join(os.path.dirname(__file__), '..', 'q2', 'sample_input.txt')
sample_output = os.path.join(os.path.dirname(__file__), '..', 'q2', 'sample_output.txt')
generated_output = os.path.join(os.path.dirname(__file__), '..', 'q2', 'output.txt')

evaluate_file(sample_input)

with open(os.path.abspath(sample_output), encoding="utf-8") as ef:
    expected = ef.read()
with open(os.path.abspath(generated_output), encoding="utf-8") as af:
    actual = af.read()

assert expected == actual, (
    f"Output does not match sample byte-for-byte.\n"
    f"Expected ({len(expected)} chars):\n{expected!r}\n\n"
    f"Got ({len(actual)} chars):\n{actual!r}"
)


# ── evaluate() result tests ──────────────────────────────────────────────────

def eval_expr(expr):
    """Helper: parse and evaluate an expression."""
    tree, _ = parse(expr)
    return evaluate(tree)

# Basic operations
assert eval_expr("3 + 5") == 8.0
assert eval_expr("10 - 3") == 7.0
assert eval_expr("4 * 5") == 20.0
assert eval_expr("10 / 4") == 2.5

# Left-associativity: 10 - 5 - 2 must evaluate to 3 (not 7)
result = eval_expr("10 - 5 - 2")
assert result == 3.0, f"Expected 3.0 (left-assoc), got {result}"

# Operator precedence: 2 + 3 * 4 = 14 (not 20)
assert eval_expr("2 + 3 * 4") == 14.0

# Negation
assert eval_expr("-5") == -5.0
assert eval_expr("--5") == 5.0
assert eval_expr("-(3+4)") == -7.0
assert eval_expr("-(-5)") == 5.0

# Complex expression matching sample
assert eval_expr("(10 - 2) * 3 + -4 / 2") == 22.0

# Implicit multiplication
assert eval_expr("2(3+4)") == 14.0


# ── Division by zero — evaluate raises ParseError ────────────────────────────
div_zero_tree, _ = parse("1 / 0")
assert raises(ParseError, evaluate, div_zero_tree), \
    "Expected ParseError for division by zero"


# ── format_result dedicated tests (whole number and decimal) ─────────────────
assert format_result(8.0)   == "8",      f"Got {format_result(8.0)!r}"
assert format_result(8.5)   == "8.5",    f"Got {format_result(8.5)!r}"
assert format_result(1/3)   == "0.3333", f"Got {format_result(1/3)!r}"
assert format_result(-7.0)  == "-7",     f"Got {format_result(-7.0)!r}"
assert format_result(0.0)   == "0",      f"Got {format_result(0.0)!r}"
assert format_result(22.0)  == "22",     f"Got {format_result(22.0)!r}"
assert format_result(2.5)   == "2.5",    f"Got {format_result(2.5)!r}"


# ── evaluate_file return value structure ─────────────────────────────────────
results = evaluate_file(sample_input)

assert len(results) == 7, f"Expected 7 results, got {len(results)}"

# "3 + 5" → result is 8.0
assert results[0]["input"] == "3 + 5"
assert results[0]["result"] == 8.0
assert results[0]["tree"] == "(+ 3 5)"

# "3 @ 5" → all ERROR
assert results[5]["input"] == "3 @ 5"
assert results[5]["result"] == "ERROR"
assert results[5]["tree"] == "ERROR"
assert results[5]["tokens"] == "ERROR"

# "1 / 0" → tree and tokens are valid strings, result is ERROR
assert results[6]["input"] == "1 / 0"
assert results[6]["result"] == "ERROR"
assert results[6]["tree"] == "(/ 1 0)",    f"Expected valid tree, got {results[6]['tree']!r}"
assert results[6]["tokens"] != "ERROR",    "Tokens should be valid for 1/0, not ERROR"


if __name__ == "__main__":
    print("All evaluator tests passed.")
