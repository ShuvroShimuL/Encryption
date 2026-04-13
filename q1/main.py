"""Q1 main — file I/O orchestration and user interaction."""

import sys
import os
from cipher import encrypt_char, encrypt_text, decrypt_text

Q1_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(Q1_DIR, "raw_text.txt")
ENC_PATH = os.path.join(Q1_DIR, "encrypted_text.txt")
DEC_PATH = os.path.join(Q1_DIR, "decrypted_text.txt")


def get_shift_input(prompt: str) -> int:
    """Prompt the user until a valid integer is entered."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print(f"  ERROR: '{raw}' is not a valid integer. Please try again.")


def check_shifts_safe(text: str, shift1: int, shift2: int) -> list:
    """Check if the chosen shifts cause any two characters in text to collide.

    Returns a list of collision descriptions (empty list = no collisions).
    A collision means two different source characters encrypt to the same
    cipher character, making decryption ambiguous.
    """
    collisions = []
    enc_map = {}
    for c in text:
        if not c.isalpha():
            continue
        e = encrypt_char(c, shift1, shift2)
        if e in enc_map and enc_map[e] != c:
            desc = f"  '{c}' and '{enc_map[e]}' both encrypt to '{e}'"
            if desc not in collisions:
                collisions.append(desc)
        else:
            enc_map[e] = c
    return collisions


def encrypt_file(shift1: int, shift2: int) -> None:
    """Read raw_text.txt, encrypt contents, write to encrypted_text.txt."""
    try:
        with open(RAW_PATH, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: '{RAW_PATH}' not found. Cannot encrypt.")
        sys.exit(1)

    encrypted = encrypt_text(text, shift1, shift2)

    with open(ENC_PATH, "w", encoding="utf-8") as f:
        f.write(encrypted)

    print(f"  [OK] Encrypted -> {ENC_PATH}")


def decrypt_file(shift1: int, shift2: int) -> None:
    """Read encrypted_text.txt, decrypt contents, write to decrypted_text.txt."""
    try:
        with open(ENC_PATH, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: '{ENC_PATH}' not found. Run encryption first.")
        sys.exit(1)

    decrypted = decrypt_text(text, shift1, shift2)

    with open(DEC_PATH, "w", encoding="utf-8") as f:
        f.write(decrypted)

    print(f"  [OK] Decrypted -> {DEC_PATH}")


def verify() -> None:
    """Compare raw_text.txt with decrypted_text.txt line by line."""
    try:
        with open(RAW_PATH, encoding="utf-8") as f:
            original_lines = f.readlines()
        with open(DEC_PATH, encoding="utf-8") as f:
            decrypted_lines = f.readlines()
    except FileNotFoundError as e:
        print(f"Error during verification: {e}")
        sys.exit(1)

    if len(original_lines) != len(decrypted_lines):
        print(
            f"  [FAIL] line count mismatch: "
            f"original={len(original_lines)}, decrypted={len(decrypted_lines)}"
        )
        return

    for i, (expected, got) in enumerate(zip(original_lines, decrypted_lines), start=1):
        if expected != got:
            print(f"  [FAIL] mismatch on line {i}")
            print(f"    expected: {repr(expected)}")
            print(f"    got:      {repr(got)}")
            return

    print("  PASS - decryption matches original exactly")


if __name__ == "__main__":
    print("=== Q1: Custom Cipher ===\n")

    # Read raw text once upfront for collision checking
    try:
        with open(RAW_PATH, encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: '{RAW_PATH}' not found.")
        sys.exit(1)

    # Keep prompting until the user picks collision-free shifts
    while True:
        shift1 = get_shift_input("Enter shift1 (integer): ")
        shift2 = get_shift_input("Enter shift2 (integer): ")

        collisions = check_shifts_safe(raw_text, shift1, shift2)
        if not collisions:
            print(f"  [OK] Shifts ({shift1}, {shift2}) are safe for this text.\n")
            break
        else:
            print(f"\n  [WARNING] Shifts ({shift1}, {shift2}) cause ambiguous encryption.")
            print(f"  These characters in the text encrypt to the same cipher letter,")
            print(f"  making perfect decryption impossible:")
            for desc in collisions[:5]:
                print(f"   {desc}")
            if len(collisions) > 5:
                print(f"  ... and {len(collisions) - 5} more collision(s).")
            print(f"\n  Tip: try shift1=2, shift2=8 (proven safe for this text).")
            print(f"  Please enter new shift values:\n")

    print("[1/3] Encrypting...")
    encrypt_file(shift1, shift2)

    print("[2/3] Decrypting...")
    decrypt_file(shift1, shift2)

    print("[3/3] Verifying...")
    verify()
