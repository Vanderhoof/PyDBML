from textwrap import indent

from pydbml._classes.enum import EnumItem
from pydbml.classes import Enum
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer
from pydbml.renderer.sql.default.utils import comment_to_sql


def get_full_name_for_sql(model: Enum) -> str:
    if model.schema == 'public':
        return f'"{model.name}"'
    else:
        return f'"{model.schema}"."{model.name}"'


@DefaultSQLRenderer.renderer_for(Enum)
def render_enum(model: Enum) -> str:
    '''
    Returns SQL for enum type:

    CREATE TYPE "job_status" AS ENUM (
      'created',
      'running',
      'done',
      'failure',
    );
    '''

    result = comment_to_sql(model.comment) if model.comment else ''
    result += f'CREATE TYPE {get_full_name_for_sql(model)} AS ENUM (\n'
    result += '\n'.join(f'{indent(i.sql, "  ")}' for i in model.items)
    result += '\n);'
    return result


@DefaultSQLRenderer.renderer_for(EnumItem)
def render_enum_item(model: EnumItem) -> str:
    result = comment_to_sql(model.comment) if model.comment else ''
    result += f"'{model.name}',"
    return result
