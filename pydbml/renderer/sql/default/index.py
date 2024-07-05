from typing import Any

from pydbml.classes import Expression, Index, Column
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer
from pydbml.renderer.sql.default.utils import comment_to_sql


def render_subject(subject: Any) -> str:
    if isinstance(subject, Column):
        return f'"{subject.name}"'
    elif isinstance(subject, Expression):
        return DefaultSQLRenderer.render(subject)
    else:
        return subject


@DefaultSQLRenderer.renderer_for(Index)
def render_index(model: Index) -> str:
    '''
    Returns inline SQL of the index to be created separately from table
    definition:

    CREATE UNIQUE INDEX ON "products" USING HASH ("id");

    But if it's a (composite) primary key index, returns an inline SQL for
    composite primary key to be used inside table definition:

    PRIMARY KEY ("id", "name")
    '''

    keys = ', '.join(render_subject(s) for s in model.subjects)

    if model.pk:
        result = comment_to_sql(model.comment) if model.comment else ''
        result += f'PRIMARY KEY ({keys})'
        return result

    components = ['CREATE']
    if model.unique:
        components.append('UNIQUE')

    components.append('INDEX')

    if model.name:
        components.append(f'"{model.name}"')

    table_name = model.table.name if model.table else ''
    components.append(f'ON "{table_name}"')

    if model.type:
        components.append(f'USING {model.type.upper()}')
    components.append(f'({keys})')
    result = comment_to_sql(model.comment) if model.comment else ''
    result += ' '.join(components) + ';'
    return result
