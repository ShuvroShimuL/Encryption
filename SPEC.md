# Assignment 2 — Specification Contract

This document defines the exact technical contract for all implementations.

---

## Question 1 — Cipher Specification

### Cipher Table

| Character Range | Encrypt Operation | Decrypt Operation |
|---|---|---|
| `a–m` (lowercase, first half) | `+ (shift1 × shift2) mod 26` | `− (shift1 × shift2) mod 26` |
| `n–z` (lowercase, second half) | `− (shift1 + shift2) mod 26` | `+ (shift1 + shift2) mod 26` |
| `A–M` (uppercase, first half) | `− shift1 mod 26` | `+ shift1 mod 26` |
| `N–Z` (uppercase, second half) | `+ (shift2²) mod 26` | `− (shift2²) mod 26` |
| All other characters | unchanged | unchanged |

### Alphabetic Index
- Lowercase: `a=0, b=1, ..., z=25` — use `ord(c) - ord('a')`
- Uppercase: `A=0, B=1, ..., Z=25` — use `ord(c) - ord('A')`
- Result must always wrap within its case range via `% 26`

### File Flow
```
raw_text.txt → [encrypt] → encrypted_text.txt → [decrypt] → decrypted_text.txt
```
`verify()` compares `raw_text.txt` vs `decrypted_text.txt` line by line using `zip()`.

---

## Question 2 — Evaluator Specification

### Formal Grammar

```
expr    → term (('+' | '-') term)*           ← left-associative, WHILE loop
term    → unary (('*' | '/') unary)*         ← left-associative, WHILE loop
unary   → '-' unary | primary                ← right-recursive (handles --5)
primary → NUMBER
        | '(' expr ')'
        | primary '(' expr ')'               ← implicit multiplication: 2(3+4)
```

### Token Types

| Type | Value | Example |
|---|---|---|
| `NUM` | `float` | `{"type": "NUM", "value": 3.0}` |
| `OP` | `+`, `-`, `*`, `/` | `{"type": "OP", "value": "+"}` |
| `LPAREN` | `(` | `{"type": "LPAREN", "value": "("}` |
| `RPAREN` | `)` | `{"type": "RPAREN", "value": ")"}` |
| `END` | `None` | `{"type": "END", "value": None}` |

**Critical:** `-` is ALWAYS an `OP` token. Never fold into `NUM`.
- `-5` → `[OP:-][NUM:5.0][END]`, NOT `[NUM:-5.0][END]`

### AST Node Schema

```python
{"type": "NUM",  "value": float}
{"type": "BIN",  "op": str, "left": node, "right": node}
{"type": "NEG",  "operand": node}
```

### Parser State Contract

Parser state is always a dict: `{"tokens": list[dict], "pos": int}`

```python
def peek(state):
    return state["tokens"][state["pos"]]

def consume(state, expected_type=None):
    token = state["tokens"][state["pos"]]
    if expected_type and token["type"] != expected_type:
        raise ParseError(f"Expected {expected_type}, got {token['type']}")
    state["pos"] += 1
    return token
```

### Implicit Multiplication Trigger Table

| Left token | Right token | Action |
|---|---|---|
| `NUM` | `LPAREN` | Inject `BIN *` node in `parse_primary` |
| `RPAREN` | `LPAREN` | Inject `BIN *` node in `parse_primary` |
| `NUM` | `NUM` | Raise `ParseError` — `2 3` is invalid |

### Error Cases

| Input | Expected behaviour |
|---|---|
| Unknown character (e.g. `@`) | `tree=ERROR`, `tokens=ERROR`, `result=ERROR` |
| Division by zero (`1 / 0`) | `tree` and `tokens` are VALID, only `result=ERROR` |
| Unary `+` (e.g. `+5`) | `ParseError` raised — all three fields ERROR |
| Trailing tokens | `ParseError` raised |

### Result Formatting

- Whole numbers (e.g. `8.0`): display as `8` (no decimal)
- Fractional numbers: round to 4 decimal places (e.g. `0.3333`)

### Output Block Format

```
Input: 3 + 5
Tree: (+ 3 5)
Tokens: [NUM:3] [OP:+] [NUM:5] [END]
Result: 8
```

- Blocks separated by exactly **one blank line**
- **No trailing newline** after the last block
- Output file: `output.txt` in same directory as input file

### Tree String Format

| Node | Format |
|---|---|
| `NUM` | Integer if whole, otherwise float |
| `BIN` | `(op left right)` |
| `NEG` | `(neg operand)` |

### Public Interface (Required by Assignment)

```python
# q2/evaluator.py
def evaluate_file(input_path: str) -> list[dict]:
    """
    Evaluates all expressions in input_path, writes output.txt.
    Returns a list of result dicts, one per expression:
    {"input": str, "tree": str, "tokens": str, "result": float | "ERROR"}
    """
```

### Module Dependency Map

```
evaluator.py  ← formatter.py ← parser.py ← tokenizer.py ← errors.py
              ← parser.py
              ← tokenizer.py
```
