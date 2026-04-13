"""Tests for q2/tokenizer.py — plain assert only."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'q2'))
from tokenizer import tokenize
from errors import ParseError


def raises(exc_type, fn, *args, **kwargs):
    """Return True if fn(*args) raises exc_type, else False."""
    try:
        fn(*args, **kwargs)
        return False
    except exc_type:
        return True


# ── "3 + 5" → correct full token list ───────────────────────────────────────
toks = tokenize("3 + 5")
assert len(toks) == 4, f"Expected 4 tokens, got {len(toks)}"
assert toks[0] == {"type": "NUM", "value": 3.0}
assert toks[1] == {"type": "OP",  "value": "+"}
assert toks[2] == {"type": "NUM", "value": 5.0}
assert toks[3] == {"type": "END", "value": None}


# ── "-5" → [OP:-][NUM:5.0] — never folded ───────────────────────────────────
toks = tokenize("-5")
assert len(toks) == 3, f"Expected 3 tokens, got {len(toks)}"
assert toks[0] == {"type": "OP",  "value": "-"}
assert toks[1] == {"type": "NUM", "value": 5.0}
assert toks[2] == {"type": "END", "value": None}


# ── "--5" → [OP:-][OP:-][NUM:5.0] ───────────────────────────────────────────
toks = tokenize("--5")
assert toks[0] == {"type": "OP", "value": "-"}
assert toks[1] == {"type": "OP", "value": "-"}
assert toks[2] == {"type": "NUM", "value": 5.0}
assert toks[3] == {"type": "END", "value": None}


# ── "3.14" → single NUM with value 3.14 ─────────────────────────────────────
toks = tokenize("3.14")
assert len(toks) == 2
assert toks[0]["type"] == "NUM"
assert abs(toks[0]["value"] - 3.14) < 1e-9


# ── "3.5.6" → raises ParseError ─────────────────────────────────────────────
assert raises(ParseError, tokenize, "3.5.6"), "Expected ParseError for '3.5.6'"


# ── "@" → raises ParseError ──────────────────────────────────────────────────
assert raises(ParseError, tokenize, "@"), "Expected ParseError for '@'"
assert raises(ParseError, tokenize, "3 @ 5"), "Expected ParseError for '3 @ 5'"


# ── "" (empty) → just [END] ──────────────────────────────────────────────────
toks = tokenize("")
assert len(toks) == 1
assert toks[0] == {"type": "END", "value": None}


# ── "   " (spaces only) → just [END] ────────────────────────────────────────
toks = tokenize("   ")
assert len(toks) == 1
assert toks[0] == {"type": "END", "value": None}


# ── LPAREN and RPAREN tokens ──────────────────────────────────────────────────
toks = tokenize("(3+5)")
assert toks[0] == {"type": "LPAREN", "value": "("}
assert toks[4] == {"type": "RPAREN", "value": ")"}


# ── All four operators tokenize correctly ────────────────────────────────────
for op in ('+', '-', '*', '/'):
    toks = tokenize(f"1 {op} 2")
    assert toks[1] == {"type": "OP", "value": op}, f"OP {op!r} mismatch"


# ── Whitespace ignored between tokens ────────────────────────────────────────
t1 = tokenize("1+2")
t2 = tokenize("1 + 2")
t3 = tokenize("  1  +  2  ")
assert t1 == t2 == t3, "Whitespace should not affect token output"


# ── Decimal starting with digit, e.g. "0.5" ─────────────────────────────────
toks = tokenize("0.5")
assert toks[0]["type"] == "NUM"
assert abs(toks[0]["value"] - 0.5) < 1e-9


# ── Complex expression tokenizes correctly ───────────────────────────────────
# "(10 - 2) * 3 + -4 / 2"
toks = tokenize("(10 - 2) * 3 + -4 / 2")
types = [t["type"] for t in toks]
assert types == ["LPAREN", "NUM", "OP", "NUM", "RPAREN",
                 "OP", "NUM", "OP", "OP", "NUM", "OP", "NUM", "END"]


if __name__ == "__main__":
    print("All tokenizer tests passed.")
