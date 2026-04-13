# Assignment 2 — Specification Contract

This document defines the exact technical contract for all implementations.

---

## Question 1 — Cipher Specification

### Cipher Table

Each half of the alphabet is a **closed group under mod 13**. A letter from one
half always encrypts to a letter in the same half, guaranteeing bijection and
perfect round-trips for **all** shift values.

| Character Range | Half size | Encrypt Operation | Decrypt Operation |
|---|---|---|---|
| `a–m` (lowercase, first half) | 13 | `+ (shift1 × shift2) mod 13` | `− (shift1 × shift2) mod 13` |
| `n–z` (lowercase, second half) | 13 | `− (shift1 + shift2) mod 13` | `+ (shift1 + shift2) mod 13` |
| `A–M` (uppercase, first half) | 13 | `− shift1 mod 13` | `+ shift1 mod 13` |
| `N–Z` (uppercase, second half) | 13 | `+ (shift2²) mod 13` | `− (shift2²) mod 13` |
| All other characters | — | unchanged | unchanged |

### Alphabetic Index (per half)
- `a–m`: index `0–12` via `ord(c) - ord('a')`, result base `ord('a')`
- `n–z`: index `0–12` via `ord(c) - ord('n')`, result base `ord('n')`
- `A–M`: index `0–12` via `ord(c) - ord('A')`, result base `ord('A')`
- `N–Z`: index `0–12` via `ord(c) - ord('N')`, result base `ord('N')`
- All shifts wrap within the half via `% 13` — never cross into the other half.

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

---

## Requirement-to-Function Mapping

This table maps every graded assignment requirement to the exact file and
function(s) that implement it.

### Question 1 — Cipher

| Requirement | File | Function(s) |
|---|---|---|
| `a–m` encrypt forward by `(shift1 × shift2) mod 13` | `q1/cipher.py` | `encrypt_char()` |
| `n–z` encrypt backward by `(shift1 + shift2) mod 13` | `q1/cipher.py` | `encrypt_char()` |
| `A–M` encrypt backward by `shift1 mod 13` | `q1/cipher.py` | `encrypt_char()` |
| `N–Z` encrypt forward by `(shift2²) mod 13` | `q1/cipher.py` | `encrypt_char()` |
| All halves decrypt inverse (perfect round-trip, all shifts) | `q1/cipher.py` | `decrypt_char()` |
| Non-alpha characters pass through unchanged | `q1/cipher.py` | `encrypt_char()`, `decrypt_char()` |
| Full text encrypt / decrypt via generator expression | `q1/cipher.py` | `encrypt_text()`, `decrypt_text()` |
| Shift input validation — loop until valid integer | `q1/main.py` | `get_shift_input()` |
| Read `raw_text.txt`, write `encrypted_text.txt` | `q1/main.py` | `encrypt_file()` |
| Read `encrypted_text.txt`, write `decrypted_text.txt` | `q1/main.py` | `decrypt_file()` |
| Display encrypted and decrypted content to console | `q1/main.py` | `encrypt_file()`, `decrypt_file()` |
| Line-by-line round-trip verification using `zip()` | `q1/main.py` | `verify()` |
| `FileNotFoundError` handling with `sys.exit(1)` | `q1/main.py` | `encrypt_file()`, `decrypt_file()`, `verify()` |
| All Q1 unit tests (plain `assert`, no frameworks) | `tests/test_cipher.py` | All `assert` statements |

### Question 2 — Evaluator

| Requirement | File | Function(s) |
|---|---|---|
| Token types: `NUM`, `OP`, `LPAREN`, `RPAREN`, `END` | `q2/tokenizer.py` | `tokenize()` |
| `-` always tokenised as `OP`, never folded into `NUM` | `q2/tokenizer.py` | `tokenize()` |
| Decimal number handling with double-dot `ParseError` | `q2/tokenizer.py` | `tokenize()` |
| Unknown character raises `ParseError` | `q2/errors.py`, `q2/tokenizer.py` | `ParseError`, `tokenize()` |
| AST node schema (`NUM`, `BIN`, `NEG`) | `q2/parser.py` | `parse()`, all parse functions |
| Left-associative addition/subtraction (while loop) | `q2/parser.py` | `parse_expr()` |
| Left-associative multiplication/division (while loop) | `q2/parser.py` | `parse_term()` |
| Right-recursive unary negation (handles `--5`) | `q2/parser.py` | `parse_unary()` |
| Unary `+` rejected with `ParseError` | `q2/parser.py` | `parse_unary()` |
| Implicit multiplication: `2(3+4)` → `BIN *` | `q2/parser.py` | `parse_primary()`, `_parse_implicit_mul()` |
| Trailing token check after full parse | `q2/parser.py` | `parse()` |
| `peek()` / `consume()` state helpers (exact contract) | `q2/parser.py` | `peek()`, `consume()` |
| Tree string: `(op left right)` / `(neg x)` / number | `q2/formatter.py` | `format_tree()` |
| Token string: `[TYPE:val]` joined by spaces | `q2/formatter.py` | `format_tokens()` |
| Result: whole numbers no decimal, others 4 d.p. | `q2/formatter.py` | `format_result()` |
| Four-line output block rendering | `q2/formatter.py` | `format_block()` |
| Recursive AST evaluation (`+`, `-`, `*`, `/`, `NEG`) | `q2/evaluator.py` | `evaluate()` |
| Division by zero raises `ParseError` | `q2/evaluator.py` | `evaluate()` |
| `1/0` special case: tree+tokens valid, result `ERROR` | `q2/evaluator.py` | `evaluate_file()` Block 2 |
| Parse failures: all three fields `ERROR` | `q2/evaluator.py` | `evaluate_file()` Block 1 |
| Output path via `os.path.abspath()` | `q2/evaluator.py` | `evaluate_file()` |
| Blocks joined by `\n\n`, file ends with `\n` | `q2/evaluator.py` | `evaluate_file()` |
| `evaluate_file()` as sole public interface | `q2/evaluator.py` | `evaluate_file()` |
| Tokenizer unit tests (plain `assert`) | `tests/test_tokenizer.py` | All `assert` statements |
| Parser unit tests (plain `assert`) | `tests/test_parser.py` | All `assert` statements |
| Evaluator tests incl. byte-for-byte output match | `tests/test_evaluator.py` | All `assert` statements |
