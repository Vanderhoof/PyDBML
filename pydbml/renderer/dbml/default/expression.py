from pydbml.classes import Expression
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer


@DefaultDBMLRenderer.renderer_for(Expression)
def render_expression(model: Expression) -> str:
    return f'`{model.text}`'
