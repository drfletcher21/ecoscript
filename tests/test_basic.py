import sys
import importlib


def test_imports_exist():
    # Ensure core modules import without error
    modules = ["tokenizer", "parser", "evaluator", "cli"]
    for m in modules:
        mod = importlib.import_module(m)
        assert hasattr(mod, "__file__")
