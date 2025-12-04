"""EcoScript minimal interpreter package (MVP)

This is a small prototype interpreter for EcoScript supporting a minimal subset:
- let variable assignment
- arithmetic and boolean expressions
- print()
- function definition and calls
- if/else and while
- blocks with braces { }

Note: This MVP uses braces for blocks to simplify the prototype. Later iterations will add indentation-aware parsing.
"""
from .cli import main

__all__ = ["tokenizer", "parser", "evaluator", "cli"]
