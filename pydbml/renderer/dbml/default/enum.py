from textwrap import indent

from pydbml.classes import Enum, EnumItem
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml, note_option_to_dbml
from pydbml.renderer.sql.default.utils import get_full_name_for_sql


@DefaultDBMLRenderer.renderer_for(Enum)
def render_enum(model: Enum) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += f'Enum {get_full_name_for_sql(model)} {{\n'
    items_str = '\n'.join(DefaultDBMLRenderer.render(i) for i in model.items)
    result += indent(items_str, '    ')
    result += '\n}'
    return result


@DefaultDBMLRenderer.renderer_for(EnumItem)
def render_enum_item(model: EnumItem) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += f'"{model.name}"'
    if model.note:
        result += f' [{note_option_to_dbml(model.note)}]'
    return result
