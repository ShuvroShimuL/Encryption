# HIT137 Group Assignment 2 — S1 2026

## Overview

This repository contains the solution for HIT137 Group Assignment 2.

## Structure

```
q1/             — Question 1: Custom text encryption/decryption
q2/             — Question 2: Recursive descent math expression evaluator
tests/          — All unit tests (plain assert, no third-party frameworks)
SPEC.md         — Full specification contract with cipher tables and grammar
PROJECT_RULES.md — Coding rules enforced across all modules
github_link.txt — Repository URL for submission
```

## Question 1 — Custom Cipher

Encrypts and decrypts `q1/raw_text.txt` using a two-shift algorithm.

**Run:**
```bash
python q1/main.py
# Enter shift1 and shift2 when prompted (e.g. 3 and 5)
# Produces: q1/encrypted_text.txt, q1/decrypted_text.txt
# Prints:   PASS — decryption matches original exactly
```

**Test:**
```bash
python tests/test_cipher.py
```

## Question 2 — Math Expression Evaluator

Reads arithmetic expressions from a file and evaluates them using recursive descent parsing.

**Run:**
```bash
python q2/evaluator.py q2/sample_input.txt
# Produces: q2/output.txt
```

**Test:**
```bash
python tests/test_tokenizer.py
python tests/test_parser.py
python tests/test_evaluator.py
```

## Full Test Suite

```bash
python tests/test_cipher.py
python q1/main.py
python tests/test_tokenizer.py
python tests/test_parser.py
python q2/evaluator.py q2/sample_input.txt
python tests/test_evaluator.py
```

## Group Members

- Member A
- Member B
- Member C
