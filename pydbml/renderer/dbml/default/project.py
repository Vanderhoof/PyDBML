from textwrap import indent
from typing import Dict

from pydbml.classes import Project
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml


def render_items(items: Dict[str, str]) -> str:
    items_str = ''
    for k, v in items.items():
        if '\n' in v:
            items_str += f"{k}: '''{v}'''\n"
        else:
            items_str += f"{k}: '{v}'\n"
    return indent(items_str.rstrip('\n'), '    ') + '\n'


@DefaultDBMLRenderer.renderer_for(Project)
def render_project(model: Project) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += f'Project "{model.name}" {{\n'
    result += render_items(model.items)
    if model.note:
        result += indent(DefaultDBMLRenderer.render(model.note), '    ') + '\n'
    result += '}'
    return result
