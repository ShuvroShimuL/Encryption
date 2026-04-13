"""Pure cipher functions for Q1 — zero I/O, zero prints."""


def encrypt_char(c: str, shift1: int, shift2: int) -> str:
    """Encrypt a single character using the two-shift cipher rules."""
    if 'a' <= c <= 'm':
        shifted = (ord(c) - ord('a') + (shift1 * shift2)) % 26
        return chr(shifted + ord('a'))
    elif 'n' <= c <= 'z':
        shifted = (ord(c) - ord('a') - (shift1 + shift2)) % 26
        return chr(shifted + ord('a'))
    elif 'A' <= c <= 'M':
        shifted = (ord(c) - ord('A') - shift1) % 26
        return chr(shifted + ord('A'))
    elif 'N' <= c <= 'Z':
        shifted = (ord(c) - ord('A') + (shift2 ** 2)) % 26
        return chr(shifted + ord('A'))
    else:
        return c


def decrypt_char(c: str, shift1: int, shift2: int) -> str:
    """Decrypt a single character — algebraic inverse of encrypt_char.

    For each case, computes both possible inverses and returns the one whose
    result falls in the correct source range. When both land in-range
    (a genuine collision from the cipher's design), the n-z / N-Z inverse
    takes priority because those rules use additive shifts that are injective
    within their own half.

    Note: This cipher can produce collisions for certain shift values —
    two source characters may encrypt to the same character. In such cases,
    decryption is deterministic but may not fully reconstruct the original.
    """
    if 'a' <= c <= 'z':
        idx = ord(c) - ord('a')
        # Inverse of a–m rule:  enc = (src + s1*s2) % 26  =>  src = (enc - s1*s2) % 26
        candidate_am = (idx - (shift1 * shift2)) % 26
        # Inverse of n–z rule:  enc = (src - s1-s2) % 26  =>  src = (enc + s1+s2) % 26
        candidate_nz = (idx + (shift1 + shift2)) % 26

        in_am = (0 <= candidate_am <= 12)
        in_nz = (13 <= candidate_nz <= 25)

        if in_am and not in_nz:
            return chr(candidate_am + ord('a'))
        if in_nz and not in_am:
            return chr(candidate_nz + ord('a'))
        if in_nz:   # both in range → collision; n–z priority
            return chr(candidate_nz + ord('a'))
        # neither in range (very unusual) — return best algebraic guess
        return chr(candidate_am + ord('a'))

    elif 'A' <= c <= 'Z':
        idx = ord(c) - ord('A')
        # Inverse of A–M rule:  enc = (src - s1) % 26  =>  src = (enc + s1) % 26
        candidate_am = (idx + shift1) % 26
        # Inverse of N–Z rule:  enc = (src + s2^2) % 26  =>  src = (enc - s2^2) % 26
        candidate_nz = (idx - (shift2 ** 2)) % 26

        in_am = (0 <= candidate_am <= 12)
        in_nz = (13 <= candidate_nz <= 25)

        if in_am and not in_nz:
            return chr(candidate_am + ord('A'))
        if in_nz and not in_am:
            return chr(candidate_nz + ord('A'))
        if in_nz:   # both in range → collision; N–Z priority
            return chr(candidate_nz + ord('A'))
        return chr(candidate_am + ord('A'))

    else:
        return c


def encrypt_text(text: str, shift1: int, shift2: int) -> str:
    """Encrypt a full string, returning the encrypted version."""
    return ''.join(encrypt_char(c, shift1, shift2) for c in text)


def decrypt_text(text: str, shift1: int, shift2: int) -> str:
    """Decrypt a full string, returning the original version."""
    return ''.join(decrypt_char(c, shift1, shift2) for c in text)
