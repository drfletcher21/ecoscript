# EcoScript — Minimal MVP

EcoScript is a small educational language and prototype interpreter (MVP) focused on clear syntax and an indentation-aware block structure similar to Python.

This repository contains a minimal interpreter written in Python:

- `tokenizer.py` — line-based tokenizer that emits INDENT/DEDENT/NEWLINE tokens
- `parser.py` — recursive-descent parser producing a small AST
- `evaluator.py` — evaluator / runtime with an `Environment` and builtin functions
- `cli.py` — small CLI to run scripts or drop into a REPL

Getting started

Requirements: Python 3.10+ (recommended)

Run the CLI (from the project root `C:\ecoscript`):

```powershell
# run a script
python cli.py path\to\script.eco

# start REPL
python cli.py --repl
```

Run tests (if pytest is installed):

```powershell
python -m pytest -q
```

Contributing

See `CONTRIBUTING.md` for contribution guidelines.

License

This project uses the MIT License. See `LICENSE` for details.
