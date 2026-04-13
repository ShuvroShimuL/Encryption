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
      - Tries: parse -> evaluate -> format all fields
      - On ANY exception: tree='ERROR', tokens='ERROR', result='ERROR'

    Writes output.txt to the same directory as input_path.
    Blocks are separated by exactly one blank line. No trailing newline.

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

        # Default to ERROR
        tree_str = "ERROR"
        tokens_str = "ERROR"
        result_str = "ERROR"
        result_val = "ERROR"

        try:
            tree, tokens = parse(expr)
            tree_str = format_tree(tree)
            tokens_str = format_tokens(tokens)
            # evaluate separately so that parse errors vs eval errors differ
            val = evaluate(tree)
            result_str = format_result(val)
            result_val = val
        except Exception:
            # Any failure: set all not-yet-set fields to ERROR
            # If parse succeeded but evaluate failed (e.g. 1/0):
            # tree_str and tokens_str may already be set correctly.
            result_str = "ERROR"
            result_val = "ERROR"
            # If parse itself failed, reset tree and tokens too
            if tree_str == "ERROR" or tokens_str == "ERROR":
                tree_str = "ERROR"
                tokens_str = "ERROR"

        res = {
            "input": expr,
            "tree": tree_str,
            "tokens": tokens_str,
            "result": result_val,
        }
        results.append(res)

        if DEBUG:
            print(f"[DEBUG] {expr!r} -> tree={tree_str!r} result={result_str!r}")

    # Build output content
    blocks = []
    for res in results:
        block = format_block({
            "input": res["input"],
            "tree": res["tree"],
            "tokens": res["tokens"],
            "result": res["result"] if res["result"] == "ERROR" else format_result(res["result"]),
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
