import os
import sys
import importlib

# Make sure parent directory is on sys.path so `ecoscript` package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PARENT = os.path.abspath(os.path.join(ROOT, '..'))
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)


def test_imports_exist():
    # Ensure core package modules import without error
    modules = ["ecoscript.tokenizer", "ecoscript.parser", "ecoscript.evaluator", "ecoscript.cli"]
    for m in modules:
        mod = importlib.import_module(m)
        assert hasattr(mod, "__file__")
