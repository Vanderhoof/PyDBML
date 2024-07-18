from textwrap import indent
from typing import List

from pydbml.constants import MANY_TO_ONE, ONE_TO_ONE, ONE_TO_MANY
from pydbml.classes import Table, Reference, Column
from pydbml.exceptions import UnknownDatabaseError
from pydbml.renderer.sql.default.note import prepare_text_for_sql
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer
from pydbml.renderer.sql.default.utils import comment_to_sql, get_full_name_for_sql


def get_references_for_sql(model: Table) -> List[Reference]:
    """
    Return all references in the database where this table is on the left side of SQL
    reference definition.
    """
    if not model.database:
        raise UnknownDatabaseError(f'Database for the table {model} is not set')
    result = []
    for ref in model.database.refs:
        if (ref.type in (MANY_TO_ONE, ONE_TO_ONE)) and\
                (ref.table1 == model):
            result.append(ref)
        elif (ref.type == ONE_TO_MANY) and (ref.table2 == model):
            result.append(ref)
    return result


def get_inline_references_for_sql(model: Table) -> List[Reference]:
    '''
    Return inline references for this table sql definition
    '''
    if model.abstract:
        return []
    return [r for r in get_references_for_sql(model) if r.inline]


def create_body(model: Table) -> str:
    body: List[str] = []
    body.extend(indent(DefaultSQLRenderer.render(c), "  ") for c in model.columns)
    body.extend(indent(DefaultSQLRenderer.render(i), "  ") for i in model.indexes if i.pk)
    body.extend(indent(DefaultSQLRenderer.render(r), "  ") for r in get_inline_references_for_sql(model))

    if model._has_composite_pk():
        body.append(
            "  PRIMARY KEY ("
            + ', '.join(f'"{c.name}"' for c in model.columns if c.pk)
            + ')')

    return ',\n'.join(body)


def create_components(model: Table) -> str:
    components = [comment_to_sql(model.comment)] if model.comment else []
    components.append(f'CREATE TABLE {get_full_name_for_sql(model)} (')

    body = create_body(model)

    components.append(body)
    components.append(');')
    components.extend('\n' + DefaultSQLRenderer.render(i) for i in model.indexes if not i.pk)

    return '\n'.join(components)


def render_column_notes(model: Table) -> str:
    result = ''
    for col in model.columns:
        if col.note:
            quoted_note = f"'{prepare_text_for_sql(col.note)}'"
            note_sql = f'COMMENT ON COLUMN "{model.name}"."{col.name}" IS {quoted_note};'
            result += f'\n\n{note_sql}'
    return result


@DefaultSQLRenderer.renderer_for(Table)
def render_table(model: Table) -> str:
    '''
    Returns full SQL for table definition:

    CREATE TABLE "countries" (
      "code" int PRIMARY KEY,
      "name" varchar,
      "continent_name" varchar
    );

    Also returns indexes if they were defined:

    CREATE INDEX ON "products" ("id", "name");
    '''
    result = create_components(model)

    if model.note:
        result += f'\n\n{model.note.sql}'

    result += render_column_notes(model)
    return result
