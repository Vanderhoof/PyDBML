from unittest import TestCase

from pydbml.classes import Expression


def test_str(expression1: Expression) -> None:
    assert str(expression1) == 'SUM(amount)'


def test_repr(expression1: Expression) -> None:
    assert repr(expression1) == "Expression('SUM(amount)')"
