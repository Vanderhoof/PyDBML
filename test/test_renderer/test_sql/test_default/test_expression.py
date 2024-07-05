from pydbml.classes import Expression
from pydbml.renderer.sql.default import render_expression


def test_render_expression(expression1: Expression):
    assert render_expression(expression1) == '(SUM(amount))'
