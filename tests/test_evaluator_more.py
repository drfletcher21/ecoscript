import os
import sys

# Make sure parent directory is on sys.path so `ecoscript` package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PARENT = os.path.abspath(os.path.join(ROOT, '..'))
if PARENT not in sys.path:
  sys.path.insert(0, PARENT)

import pytest
import textwrap

try:
  from ecoscript.evaluator import Evaluator # type: ignore
except Exception:
  # If import fails, raise so pytest will show a helpful error
  raise


def test_arithmetic_and_let(capsys):
    src = textwrap.dedent("""
    let a = 5
    let b = 2
    print(a * b + 3)
    """)
    Evaluator().run_source(src)
    out = capsys.readouterr().out
    assert out.strip() == "13"


def test_if_else_and_while(capsys):
    src = textwrap.dedent("""
    let i = 0
    while (i < 3)
      if (i % 2 == 0)
        print("even")
      else
        print("odd")
      let i = i + 1
    """)
    Evaluator().run_source(src)
    out_lines = [l.strip() for l in capsys.readouterr().out.splitlines() if l.strip()]
    assert out_lines == ["even", "odd", "even"]


def test_function_and_return(capsys):
    src = textwrap.dedent("""
    function add(x, y)
      return x + y
    print(add(2, 3))
    """)
    Evaluator().run_source(src)
    out = capsys.readouterr().out
    assert out.strip() == "5"


def test_recursion_factorial(capsys):
    src = textwrap.dedent("""
    function fact(n)
      if (n <= 1)
        return 1
      return n * fact(n - 1)
    print(fact(5))
    """)
    Evaluator().run_source(src)
    out = capsys.readouterr().out
    assert out.strip() == "120"


def test_closure_and_environment(capsys):
    src = textwrap.dedent("""
    function make_adder(x)
      function inner(y)
        return x + y
      return inner
    let add5 = make_adder(5)
    print(add5(3))
    """)
    Evaluator().run_source(src)
    out = capsys.readouterr().out
    assert out.strip() == "8"
