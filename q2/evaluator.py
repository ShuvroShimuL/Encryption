"""Evaluator for Q2 — public entry point: evaluate_file().

This module wires together tokenizer, parser, formatter and handles file I/O.
It is the ONLY public interface required by the assignment.
"""

import os
import sys

from errors import ParseError
from tokenizer import tokenize
from parser import parse
from formatter import format_tree, format_tokens, format_result, format_block

DEBUG = False


def evaluate(node: dict) -> float:
    """Recursively evaluate an AST node, returning a float result.

    Raises ParseError on division by zero or unknown node type.
    """
    if node["type"] == "NUM":
        return node["value"]

    if node["type"] == "NEG":
        return -evaluate(node["operand"])

    if node["type"] == "BIN":
        left = evaluate(node["left"])
        right = evaluate(node["right"])
        op = node["op"]
        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise ParseError("Division by zero")
            return left / right
        raise ParseError(f"Unknown operator: {op!r}")

    raise ParseError(f"Unknown AST node type: {node['type']!r}")


def evaluate_file(input_path: str) -> list:
    """Evaluate all expressions in input_path, write output.txt, return results.

    Reads lines from input_path (UTF-8). For each line:
      - Strips trailing newline only (rstrip('\\n'))
      - Block 1: parse + format tree/tokens. Any exception -> all three ERROR.
      - Block 2: evaluate only. ParseError -> result ERROR, tree/tokens valid.

    Writes output.txt to the same directory as input_path.
    Blocks are separated by exactly one blank line. Ends with a trailing newline.

    Returns a list of dicts:
      {'input': str, 'tree': str, 'tokens': str, 'result': float | 'ERROR'}
    """
    abs_input = os.path.abspath(input_path)
    out_dir = os.path.dirname(abs_input)
    out_path = os.path.join(out_dir, "output.txt")

    with open(abs_input, encoding="utf-8") as f:
        lines = f.readlines()

    results = []

    for line in lines:
        expr = line.rstrip("\n")

        tree_str = "ERROR"
        tokens_str = "ERROR"
        result_val = "ERROR"
        tree = None

        # Block 1: tokenize + parse + format tree/tokens
        # Any failure here means the expression is malformed → all three ERROR
        try:
            tree, tokens = parse(expr)
            tree_str = format_tree(tree)
            tokens_str = format_tokens(tokens)
        except (ParseError, Exception):
            tree_str = "ERROR"
            tokens_str = "ERROR"
            result_val = "ERROR"
            results.append({
                "input": expr,
                "tree": "ERROR",
                "tokens": "ERROR",
                "result": "ERROR",
            })
            if DEBUG:
                print(f"[DEBUG] parse error for {expr!r}")
            continue

        # Block 2: evaluate — only catches ParseError (e.g. division by zero)
        # tree_str and tokens_str are already correctly set from Block 1
        try:
            result_val = evaluate(tree)
        except ParseError:
            result_val = "ERROR"

        results.append({
            "input": expr,
            "tree": tree_str,
            "tokens": tokens_str,
            "result": result_val,
        })

        if DEBUG:
            print(f"[DEBUG] {expr!r} -> tree={tree_str!r} result={result_val!r}")

    # Build output file
    blocks = []
    for res in results:
        r = res["result"]
        block = format_block({
            "input": res["input"],
            "tree": res["tree"],
            "tokens": res["tokens"],
            "result": r if r == "ERROR" else format_result(r),
        })
        blocks.append(block)

    output_content = "\n\n".join(blocks) + "\n"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    return results



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluator.py <input_path>")
        sys.exit(1)
    evaluate_file(sys.argv[1])
