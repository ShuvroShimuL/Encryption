"""Tests for q1/cipher.py — plain assert only, no third-party frameworks.

New cipher design: each half operates within its own 13-character space (mod 13),
guaranteeing bijection and perfect round-trips for ALL shift values.

With shifts (3, 5):
  product = (3 * 5) % 13 = 15 % 13 = 2   <- a-m forward shift
  sumval  = (3 + 5) % 13 = 8             <- n-z backward shift
  s1mod13 = 3 % 13       = 3             <- A-M backward shift
  sq_mod13= (5**2) % 13  = 25 % 13 = 12  <- N-Z forward shift
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'q1'))
from cipher import encrypt_char, decrypt_char, encrypt_text, decrypt_text


# ── a-m rule: FORWARD by (shift1 * shift2) % 13, stays in a-m ──────────────

# 'a' (idx 0)  -> (0 + 2) % 13 = 2  -> 'c'
assert encrypt_char('a', 3, 5) == 'c', f"Got {encrypt_char('a', 3, 5)!r}"

# 'e' (idx 4)  -> (4 + 2) % 13 = 6  -> 'g'
assert encrypt_char('e', 3, 5) == 'g', f"Got {encrypt_char('e', 3, 5)!r}"

# 'm' (idx 12) -> (12 + 2) % 13 = 1 -> 'b'   (wraps within a-m)
assert encrypt_char('m', 3, 5) == 'b', f"Got {encrypt_char('m', 3, 5)!r}"


# ── n-z rule: BACKWARD by (shift1 + shift2) % 13, stays in n-z ──────────────

# 'n' (idx 0 within n-z) -> (0 - 8) % 13 = 5 -> chr(5 + ord('n')) = 's'
assert encrypt_char('n', 3, 5) == 's', f"Got {encrypt_char('n', 3, 5)!r}"

# 'z' (idx 12 within n-z) -> (12 - 8) % 13 = 4 -> chr(4 + ord('n')) = 'r'
assert encrypt_char('z', 3, 5) == 'r', f"Got {encrypt_char('z', 3, 5)!r}"

# Result is ALWAYS in n-z range
for c in 'nopqrstuvwxyz':
    e = encrypt_char(c, 3, 5)
    assert 'n' <= e <= 'z', f"n-z breach: {c!r} -> {e!r}"


# ── A-M rule: BACKWARD by shift1 % 13, stays in A-M ────────────────────────

# 'A' (idx 0)  -> (0 - 3) % 13 = 10 -> chr(10 + ord('A')) = 'K'
assert encrypt_char('A', 3, 5) == 'K', f"Got {encrypt_char('A', 3, 5)!r}"

# 'M' (idx 12) -> (12 - 3) % 13 = 9 -> chr(9 + ord('A')) = 'J'
assert encrypt_char('M', 3, 5) == 'J', f"Got {encrypt_char('M', 3, 5)!r}"

# Result is ALWAYS in A-M range
for c in 'ABCDEFGHIJKLM':
    e = encrypt_char(c, 3, 5)
    assert 'A' <= e <= 'M', f"A-M breach: {c!r} -> {e!r}"


# ── N-Z rule: FORWARD by (shift2 ** 2) % 13, stays in N-Z ───────────────────

# 'N' (idx 0 within N-Z) -> (0 + 12) % 13 = 12 -> chr(12 + ord('N')) = 'Z'
assert encrypt_char('N', 3, 5) == 'Z', f"Got {encrypt_char('N', 3, 5)!r}"

# 'Z' (idx 12 within N-Z) -> (12 + 12) % 13 = 11 -> chr(11 + ord('N')) = 'Y'
assert encrypt_char('Z', 3, 5) == 'Y', f"Got {encrypt_char('Z', 3, 5)!r}"

# Result is ALWAYS in N-Z range
for c in 'NOPQRSTUVWXYZ':
    e = encrypt_char(c, 3, 5)
    assert 'N' <= e <= 'Z', f"N-Z breach: {c!r} -> {e!r}"


# ── Non-letter passthrough ────────────────────────────────────────────────────

assert encrypt_char('3', 3, 5) == '3'
assert encrypt_char(' ', 3, 5) == ' '
assert encrypt_char('!', 3, 5) == '!'
assert encrypt_char('\n', 3, 5) == '\n'
assert encrypt_char('\t', 3, 5) == '\t'


# ── Half-boundary distinctness ────────────────────────────────────────────────

# 'm' (a-m) and 'n' (n-z) use different rules → always different result ranges
assert 'a' <= encrypt_char('m', 3, 5) <= 'm'   # stays in a-m
assert 'n' <= encrypt_char('n', 3, 5) <= 'z'   # stays in n-z

# 'M' (A-M) and 'N' (N-Z) use different rules → always different result ranges
assert 'A' <= encrypt_char('M', 3, 5) <= 'M'   # stays in A-M
assert 'N' <= encrypt_char('N', 3, 5) <= 'Z'   # stays in N-Z


# ── No cross-half collisions for any shift pair ───────────────────────────────

for shifts in [(3, 5), (1, 1), (10, 10), (2, 8), (7, 7)]:
    s1, s2 = shifts
    # Build full encryption map for all 26 lowercase letters
    enc_lower = {c: encrypt_char(c, s1, s2) for c in 'abcdefghijklmnopqrstuvwxyz'}
    # No two distinct source letters share the same encrypted letter
    enc_values = list(enc_lower.values())
    assert len(enc_values) == len(set(enc_values)), \
        f"Lowercase collision detected for shifts {shifts}: {enc_values}"

    enc_upper = {c: encrypt_char(c, s1, s2) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
    enc_values_u = list(enc_upper.values())
    assert len(enc_values_u) == len(set(enc_values_u)), \
        f"Uppercase collision detected for shifts {shifts}: {enc_values_u}"


# ── Full round-trip for ALL shifts: every letter ──────────────────────────────

for shifts in [(3, 5), (1, 1), (10, 10), (2, 8), (7, 7)]:
    s1, s2 = shifts
    for c in 'abcdefghijklmnopqrstuvwxyz':
        got = decrypt_char(encrypt_char(c, s1, s2), s1, s2)
        assert got == c, (
            f"Lowercase round-trip FAIL shifts={shifts}: "
            f"{c!r} -> {encrypt_char(c, s1, s2)!r} -> {got!r}"
        )
    for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        got = decrypt_char(encrypt_char(c, s1, s2), s1, s2)
        assert got == c, (
            f"Uppercase round-trip FAIL shifts={shifts}: "
            f"{c!r} -> {encrypt_char(c, s1, s2)!r} -> {got!r}"
        )


# ── Full text round-trips ─────────────────────────────────────────────────────

sample = "The quick brown fox jumps over the lazy dog."
for shifts in [(3, 5), (1, 1), (10, 10)]:
    s1, s2 = shifts
    encrypted = encrypt_text(sample, s1, s2)
    decrypted = decrypt_text(encrypted, s1, s2)
    assert decrypted == sample, (
        f"Text round-trip FAIL shifts={shifts}:\n"
        f"  original:  {sample!r}\n"
        f"  encrypted: {encrypted!r}\n"
        f"  decrypted: {decrypted!r}"
    )

# Non-alpha characters always pass through unchanged
passthrough = "123 !@# \n\t... 456"
for shifts in [(3, 5), (1, 1), (10, 10)]:
    s1, s2 = shifts
    assert encrypt_text(passthrough, s1, s2) == passthrough
    assert decrypt_text(passthrough, s1, s2) == passthrough


if __name__ == "__main__":
    print("All cipher tests passed.")
