"""Tests for q1/cipher.py — plain assert only, no third-party frameworks."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'q1'))
from cipher import encrypt_char, decrypt_char, encrypt_text, decrypt_text


# ── Individual rule tests (shifts 3, 5) ────────────────────────────────────

# a–m rule: shift FORWARD by shift1 * shift2 = 15
# 'a' (idx 0) → (0 + 15) % 26 = 15 → 'p'
assert encrypt_char('a', 3, 5) == 'p', f"Expected 'p', got {encrypt_char('a', 3, 5)!r}"

# 'e' (idx 4) → (4 + 15) % 26 = 19 → 't'
assert encrypt_char('e', 3, 5) == 't', f"Expected 't', got {encrypt_char('e', 3, 5)!r}"

# 'm' (idx 12) → (12 + 15) % 26 = 1 → 'b'  (boundary, wraps around)
assert encrypt_char('m', 3, 5) == 'b', f"Expected 'b', got {encrypt_char('m', 3, 5)!r}"

# n–z rule: shift BACKWARD by shift1 + shift2 = 8
# 'n' (idx 13) → (13 - 8) % 26 = 5 → 'f'
assert encrypt_char('n', 3, 5) == 'f', f"Expected 'f', got {encrypt_char('n', 3, 5)!r}"

# 'z' (idx 25) → (25 - 8) % 26 = 17 → 'r'
assert encrypt_char('z', 3, 5) == 'r', f"Expected 'r', got {encrypt_char('z', 3, 5)!r}"

# A–M rule: shift BACKWARD by shift1 = 3
# 'A' (idx 0) → (0 - 3) % 26 = 23 → 'X'
assert encrypt_char('A', 3, 5) == 'X', f"Expected 'X', got {encrypt_char('A', 3, 5)!r}"

# 'M' (idx 12) → (12 - 3) % 26 = 9 → 'J'
assert encrypt_char('M', 3, 5) == 'J', f"Expected 'J', got {encrypt_char('M', 3, 5)!r}"

# N–Z rule: shift FORWARD by shift2² = 25
# 'N' (idx 13) → (13 + 25) % 26 = 12 → 'M'  (wraps)
assert encrypt_char('N', 3, 5) == 'M', f"Expected 'M', got {encrypt_char('N', 3, 5)!r}"

# 'Z' (idx 25) → (25 + 25) % 26 = 24 → 'Y'
assert encrypt_char('Z', 3, 5) == 'Y', f"Expected 'Y', got {encrypt_char('Z', 3, 5)!r}"


# ── Non-letter passthrough ──────────────────────────────────────────────────

assert encrypt_char('3', 3, 5) == '3'
assert encrypt_char(' ', 3, 5) == ' '
assert encrypt_char('!', 3, 5) == '!'
assert encrypt_char('\n', 3, 5) == '\n'
assert encrypt_char('\t', 3, 5) == '\t'
assert encrypt_char('5', 10, 10) == '5'


# ── Boundary rule distinctness ──────────────────────────────────────────────

# 'm' and 'n' are in different halves → must produce different encrypted chars
assert encrypt_char('m', 3, 5) != encrypt_char('n', 3, 5)
# 'M' and 'N' are in different halves → must produce different encrypted chars
assert encrypt_char('M', 3, 5) != encrypt_char('N', 3, 5)


# ── Wrap-around validity ────────────────────────────────────────────────────

# With shifts (10, 10): shift1*shift2 = 100, mod 26 = 22
# 'a' → (0 + 22) % 26 = 22 → 'w' — still a valid lowercase
result_wrap = encrypt_char('a', 10, 10)
assert 'a' <= result_wrap <= 'z', f"Wrap result not lowercase: {result_wrap!r}"


# ── Round-trip tests (collision-aware) ─────────────────────────────────────
# The cipher maps different source characters to the same cipher character
# for some shift values (e.g. shifts (3,5): both 'a' and 'x' → 'p').
# This is inherent to the cipher's design — decryption is deterministic
# (prioritises a–m) but not always a perfect inverse for all 26 letters.
# We test round-trips ONLY for characters that do not collide.

def has_collision(c: str, s1: int, s2: int) -> bool:
    """Return True if another character encrypts to the same result as c."""
    target = encrypt_char(c, s1, s2)
    if 'a' <= c <= 'z':
        for i in range(26):
            other = chr(i + ord('a'))
            if other != c and encrypt_char(other, s1, s2) == target:
                return True
    elif 'A' <= c <= 'Z':
        for i in range(26):
            other = chr(i + ord('A'))
            if other != c and encrypt_char(other, s1, s2) == target:
                return True
    return False

for shifts in [(3, 5), (1, 1), (10, 10)]:
    s1, s2 = shifts
    for c in 'abcdefghijklmnopqrstuvwxyz':
        if not has_collision(c, s1, s2):
            roundtrip = decrypt_char(encrypt_char(c, s1, s2), s1, s2)
            assert roundtrip == c, (
                f"Lowercase round-trip FAIL shifts={shifts}: "
                f"{c!r} → {encrypt_char(c,s1,s2)!r} → {roundtrip!r}"
            )
    for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if not has_collision(c, s1, s2):
            roundtrip = decrypt_char(encrypt_char(c, s1, s2), s1, s2)
            assert roundtrip == c, (
                f"Uppercase round-trip FAIL shifts={shifts}: "
                f"{c!r} → {encrypt_char(c,s1,s2)!r} → {roundtrip!r}"
            )


# ── Non-alphabetic passthrough round-trip ───────────────────────────────────
# Non-alpha chars always round-trip perfectly (they pass through unchanged)
passthrough = "123 !@# \n\t... 456"
for shifts in [(3, 5), (1, 1), (10, 10)]:
    s1, s2 = shifts
    assert encrypt_text(passthrough, s1, s2) == passthrough
    assert decrypt_text(passthrough, s1, s2) == passthrough


# ── Property: encrypt and decrypt are deterministic ─────────────────────────
# Calling twice with same shifts gives same result
for s1, s2 in [(3, 5), (2, 8)]:
    for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        assert encrypt_char(c, s1, s2) == encrypt_char(c, s1, s2)
        assert decrypt_char(encrypt_char(c, s1, s2), s1, s2) == \
               decrypt_char(encrypt_char(c, s1, s2), s1, s2)



if __name__ == "__main__":
    print("All cipher tests passed.")
