from textwrap import indent

from pydbml.classes import TableGroup
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.table import get_full_name_for_dbml
from pydbml.renderer.dbml.default.utils import comment_to_dbml
from pydbml.tools import doublequote_string


@DefaultDBMLRenderer.renderer_for(TableGroup)
def render_table_group(model: TableGroup) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    quoted_name = doublequote_string(model.name)
    result += f'TableGroup {quoted_name}'
    if model.color:
        result += f' [color: {model.color}]'
    result += ' {\n'
    for i in model.items:
        result += f'    {get_full_name_for_dbml(i)}\n'
    if model.note:
        result += indent(model.note.dbml, '    ') + '\n'
    result += '}'
    return result
