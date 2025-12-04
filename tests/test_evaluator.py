import os
import sys

# Ensure the parent directory is on sys.path so the 'ecoscript' package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PARENT = os.path.abspath(os.path.join(ROOT, '..'))
if PARENT not in sys.path:
  sys.path.insert(0, PARENT)

from ecoscript.evaluator import Evaluator


def test_arithmetic_and_let():
    ev = Evaluator()
    result = ev.run_source("let x = 5\nx * 2")
    assert result == 10


def test_function_call():
    ev = Evaluator()
    src = """function add(a, b)
  return a + b
add(3, 4)
"""
    assert ev.run_source(src) == 7


def test_if_else():
    ev = Evaluator()
    src = """if (1 < 2)
  10
else
  20
"""
    assert ev.run_source(src) == 10


def test_print_capture():
    ev = Evaluator()
    out = []
    ev.global_env.set('print', lambda *a: out.append(' '.join(map(str, a))))
    ev.run_source('print(1 + 2)')
    assert out == ['3']
