# Project Rules

- Python 3.10+ only. No third-party libraries.
- No classes except `class ParseError(Exception): pass` in q2/errors.py.
- All file I/O uses encoding="utf-8".
- Q2 modules tokenizer, parser, formatter must be pure functions — no file I/O, no prints.
- File I/O lives only in evaluate_file() and q1/main.py.
- The only exception type raised across all Q2 modules is ParseError.
- Never fold unary minus into a NUM token. -5 → [OP:-][NUM:5].
- Plain assert statements for all tests. No pytest, no unittest.
- DEBUG = False must be committed. Never commit DEBUG = True.
- os.path.abspath() for all output paths. No relative paths.
