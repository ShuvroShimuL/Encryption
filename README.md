# Encryption Assignment

Two independent Python modules built from scratch — a custom text cipher and a recursive descent math expression evaluator — with a full unit test suite and no third-party dependencies.

## Structure

```
q1/              — Question 1: Custom text encryption/decryption
q2/              — Question 2: Recursive descent math expression evaluator
tests/           — Unit tests (plain assert, no third-party frameworks)
SPEC.md          — Full specification: cipher tables and expression grammar
PROJECT_RULES.md — Coding standards enforced across all modules
github_link.txt  — Repository URL for submission
```

---

## Question 1 — Two-Shift Cipher

Encrypts and decrypts `q1/raw_text.txt` using a custom two-key shift algorithm. Both shift values are supplied at runtime, making each encryption session unique. After decryption, the program self-verifies that the recovered text matches the original exactly.

**How it works:** The cipher applies two independent character shifts — `shift1` and `shift2` — to transform plaintext into ciphertext. Decryption reverses both shifts in sequence to reconstruct the original message. The cipher table is defined in [`SPEC.md`](SPEC.md).

**Run:**
```bash
python q1/main.py
# Prompts for shift1 and shift2 (e.g. 3 and 5)
# Writes:  q1/encrypted_text.txt
#          q1/decrypted_text.txt
# Prints:  PASS — decryption matches original exactly
```

**Test:**
```bash
python tests/test_cipher.py
```

---

## Question 2 — Math Expression Evaluator

Reads arithmetic expressions line-by-line from a file and evaluates each one using a hand-written recursive descent parser — no `eval()`, no parsing libraries. The parser respects standard operator precedence and parentheses grouping, following the formal grammar specified in [`SPEC.md`](SPEC.md).

**Pipeline:** `raw string → tokenizer → parser → evaluator → q2/output.txt`

**Run:**
```bash
python q2/evaluator.py q2/sample_input.txt
# Writes: q2/output.txt
```

**Test:**
```bash
python tests/test_tokenizer.py
python tests/test_parser.py
python tests/test_evaluator.py
```

---

## Full Test Suite

```bash
python tests/test_cipher.py
python q1/main.py
python tests/test_tokenizer.py
python tests/test_parser.py
python q2/evaluator.py q2/sample_input.txt
python tests/test_evaluator.py
```

All tests use plain `assert` statements — no third-party frameworks required.

---

## Group Members

- Member A
- Member B
- Member C
