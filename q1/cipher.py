"""Pure cipher functions for Q1 — zero I/O, zero prints.

Cipher design: each half of the alphabet forms a closed group under mod 13.
  - Lowercase a-m  (indices 0-12): modular arithmetic within a-m only
  - Lowercase n-z  (indices 0-12): modular arithmetic within n-z only
  - Uppercase A-M  (indices 0-12): modular arithmetic within A-M only
  - Uppercase N-Z  (indices 0-12): modular arithmetic within N-Z only

Because each half is closed under the cipher, no letter can ever encrypt
to a letter in the other half. This guarantees bijection within each half
and makes decryption a perfect mathematical inverse for ALL shift values.
"""

HALF = 13   # size of each alphabet half


def encrypt_char(c: str, shift1: int, shift2: int) -> str:
    """Encrypt a single character using the two-shift cipher rules.

    Lowercase a-m : shift FORWARD by (shift1 * shift2) mod 13, stay in a-m
    Lowercase n-z : shift BACKWARD by (shift1 + shift2) mod 13, stay in n-z
    Uppercase A-M : shift BACKWARD by shift1 mod 13, stay in A-M
    Uppercase N-Z : shift FORWARD by (shift2 ** 2) mod 13, stay in N-Z
    Other chars   : returned unchanged
    """
    if 'a' <= c <= 'm':
        idx = ord(c) - ord('a')                          # 0-12
        shifted = (idx + (shift1 * shift2)) % HALF
        return chr(shifted + ord('a'))

    elif 'n' <= c <= 'z':
        idx = ord(c) - ord('n')                          # 0-12
        shifted = (idx - (shift1 + shift2)) % HALF
        return chr(shifted + ord('n'))

    elif 'A' <= c <= 'M':
        idx = ord(c) - ord('A')                          # 0-12
        shifted = (idx - shift1) % HALF
        return chr(shifted + ord('A'))

    elif 'N' <= c <= 'Z':
        idx = ord(c) - ord('N')                          # 0-12
        shifted = (idx + (shift2 ** 2)) % HALF
        return chr(shifted + ord('N'))

    else:
        return c


def decrypt_char(c: str, shift1: int, shift2: int) -> str:
    """Decrypt a single character — exact algebraic inverse of encrypt_char.

    Because each half operates mod 13 within its own closed group, the
    inverse is a straightforward reversal of the shift arithmetic.
    """
    if 'a' <= c <= 'm':
        idx = ord(c) - ord('a')
        original = (idx - (shift1 * shift2)) % HALF
        return chr(original + ord('a'))

    elif 'n' <= c <= 'z':
        idx = ord(c) - ord('n')
        original = (idx + (shift1 + shift2)) % HALF
        return chr(original + ord('n'))

    elif 'A' <= c <= 'M':
        idx = ord(c) - ord('A')
        original = (idx + shift1) % HALF
        return chr(original + ord('A'))

    elif 'N' <= c <= 'Z':
        idx = ord(c) - ord('N')
        original = (idx - (shift2 ** 2)) % HALF
        return chr(original + ord('N'))

    else:
        return c


def encrypt_text(text: str, shift1: int, shift2: int) -> str:
    """Encrypt a full string, returning the encrypted version."""
    return ''.join(encrypt_char(c, shift1, shift2) for c in text)


def decrypt_text(text: str, shift1: int, shift2: int) -> str:
    """Decrypt a full string, returning the original version."""
    return ''.join(decrypt_char(c, shift1, shift2) for c in text)
