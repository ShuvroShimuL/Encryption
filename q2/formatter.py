"""Formatter for Q2 — pure functions, no I/O, no prints."""


def format_tree(node: dict) -> str:
    """Convert an AST node to its string representation.

    NUM: integer display if whole (e.g. 3.0 -> '3'), else float string.
    BIN: '(op left right)'
    NEG: '(neg operand)'
    """
    if node["type"] == "NUM":
        v = node["value"]
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        return str(v)

    if node["type"] == "BIN":
        left = format_tree(node["left"])
        right = format_tree(node["right"])
        return f"({node['op']} {left} {right})"

    if node["type"] == "NEG":
        return f"(neg {format_tree(node['operand'])})"

    raise ValueError(f"Unknown node type: {node['type']!r}")


def format_tokens(tokens: list) -> str:
    """Convert a token list to its display string.

    Format: '[NUM:3] [OP:+] [NUM:5] [END]'
    NUM values use the same whole-number rule as format_tree.
    Tokens are joined with a single space.
    """
    parts = []
    for tok in tokens:
        t = tok["type"]
        v = tok["value"]
        if t == "NUM":
            if abs(v - round(v)) < 1e-9:
                display = str(int(round(v)))
            else:
                display = str(v)
            parts.append(f"[NUM:{display}]")
        elif t == "END":
            parts.append("[END]")
        else:
            parts.append(f"[{t}:{v}]")
    return " ".join(parts)


def format_result(value: float) -> str:
    """Format a numeric result — whole numbers without decimal, others to 4dp."""
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return str(round(value, 4))


def format_block(result: dict) -> str:
    """Render one result dict as the 4-line output block string."""
    return (
        f"Input: {result['input']}\n"
        f"Tree: {result['tree']}\n"
        f"Tokens: {result['tokens']}\n"
        f"Result: {result['result']}"
    )
