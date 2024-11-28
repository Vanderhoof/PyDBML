from typing import Union

from pydbml.classes import Column, Enum, Expression
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml, note_option_to_dbml, quote_string, prepare_text_for_dbml
from pydbml.renderer.sql.default.utils import get_full_name_for_sql


def default_to_str(val: Union[Expression, str, int, float]) -> str:
    if isinstance(val, str):
        if val.lower() in ('null', 'true', 'false'):
            return val.lower()
        else:
            return f"'{prepare_text_for_dbml(val)}'"
    elif isinstance(val, Expression):
        return val.dbml
    else:  # int or float or bool
        return str(val)


def render_options(model: Column) -> str:
    options = [ref.dbml for ref in model.get_refs() if ref.inline]
    if model.pk:
        options.append('pk')
    if model.autoinc:
        options.append('increment')
    if model.default:
        options.append(f'default: {default_to_str(model.default)}')
    if model.unique:
        options.append('unique')
    if model.not_null:
        options.append('not null')
    if model.note:
        options.append(note_option_to_dbml(model.note))
    if model.properties:
        if model.table and model.table.database and model.table.database.allow_properties:
            for key, value in model.properties.items():
                options.append(f'{key}: {quote_string(value)}')

    if options:
        return f' [{", ".join(options)}]'
    return ''


@DefaultDBMLRenderer.renderer_for(Column)
def render_column(model: Column) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += f'"{model.name}" '
    if isinstance(model.type, Enum):
        result += get_full_name_for_sql(model.type)
    else:
        result += model.type

    result += render_options(model)
    return result
