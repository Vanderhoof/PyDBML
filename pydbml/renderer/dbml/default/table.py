import re
from textwrap import indent

from pydbml.classes import Table
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml


def get_full_name_for_dbml(model) -> str:
    if model.schema == 'public':
        return f'"{model.name}"'
    else:
        return f'"{model.schema}"."{model.name}"'


def render_header(model: Table) -> str:
    name = get_full_name_for_dbml(model)

    result = f'Table {name} '
    if model.alias:
        result += f'as "{model.alias}" '
    if model.header_color:
        result += f'[headercolor: {model.header_color}] '
    return result


def render_indexes(model: Table) -> str:
    if model.indexes:
        result = '\n    indexes {\n'
        indexes_str = '\n'.join(DefaultDBMLRenderer.render(i) for i in model.indexes)
        result += indent(indexes_str, '        ') + '\n'
        result += '    }\n'
        return result
    return ''


@DefaultDBMLRenderer.renderer_for(Table)
def render_table(model: Table) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += render_header(model)

    result += '{\n'
    columns_str = '\n'.join(DefaultDBMLRenderer.render(c) for c in model.columns)
    result += indent(columns_str, '    ') + '\n'
    if model.note:
        result += indent(model.note.dbml, '    ') + '\n'

    result += render_indexes(model)

    result += '}'
    return result
