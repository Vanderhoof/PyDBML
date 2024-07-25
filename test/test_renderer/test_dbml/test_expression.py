from pydbml.classes import Expression
from pydbml.renderer.dbml.default import render_expression


def test_render_expression(expression1: Expression) -> None:
    assert render_expression(expression1) == "`SUM(amount)`"
