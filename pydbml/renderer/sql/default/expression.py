from pydbml.classes import Expression
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer


@DefaultSQLRenderer.renderer_for(Expression)
def render_expression(model: Expression) -> str:
    return f'({model.text})'
