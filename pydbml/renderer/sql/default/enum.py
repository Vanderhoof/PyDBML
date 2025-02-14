from textwrap import indent

from pydbml._classes.enum import EnumItem
from pydbml.classes import Enum
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer
from pydbml.renderer.sql.default.utils import comment_to_sql, get_full_name_for_sql


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
    enum_body = '\n'.join(f'{indent(DefaultSQLRenderer.render(i), "  ")}' for i in model.items)
    result += enum_body.rstrip(',')
    result += '\n);'
    return result


@DefaultSQLRenderer.renderer_for(EnumItem)
def render_enum_item(model: EnumItem) -> str:
    result = comment_to_sql(model.comment) if model.comment else ''
    result += f"'{model.name}',"
    return result
