from pydbml.classes import Column, Enum, Expression
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer
from .utils import comment_to_sql
from .enum import get_full_name_for_sql as get_full_name_for_sql_enum


@DefaultSQLRenderer.renderer_for(Column)
def render_column(model: Column) -> str:
    '''
    Returns inline SQL of the column, which should be a part of table definition:

    "id" integer PRIMARY KEY AUTOINCREMENT
    '''

    components = [f'"{model.name}"']
    if isinstance(model.type, Enum):
        components.append(get_full_name_for_sql_enum(model.type))
    else:
        components.append(str(model.type))

    table_has_composite_pk = model.table._has_composite_pk() if model.table else False
    if model.pk and not table_has_composite_pk:  # composite PKs are rendered in table sql
        components.append('PRIMARY KEY')
    if model.autoinc:
        components.append('AUTOINCREMENT')
    if model.unique:
        components.append('UNIQUE')
    if model.not_null:
        components.append('NOT NULL')
    if model.default is not None:
        if isinstance(model.default, Expression):
            default = DefaultSQLRenderer.render(model.default)
        else:
            default = model.default  # type: ignore
        components.append(f'DEFAULT {default}')

    result = comment_to_sql(model.comment) if model.comment else ''
    result += ' '.join(components)
    return result
