from textwrap import indent

from pydbml.classes import Project
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml


@DefaultDBMLRenderer.renderer_for(Project)
def render_project(model: Project) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += f'Project "{model.name}" {{\n'
    if model.items:
        items_str = ''
        for k, v in model.items.items():
            if '\n' in v:
                items_str += f"{k}: '''{v}'''\n"
            else:
                items_str += f"{k}: '{v}'\n"
        result += indent(items_str[:-1], '    ') + '\n'
    if model.note:
        result += indent(DefaultDBMLRenderer.render(model.note), '    ') + '\n'
    result += '}'
    return result
