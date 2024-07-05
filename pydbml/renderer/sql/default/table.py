from textwrap import indent
from typing import List

from pydbml.constants import MANY_TO_ONE, ONE_TO_ONE, ONE_TO_MANY
from pydbml.classes import Table, Reference
from pydbml.exceptions import UnknownDatabaseError
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

    model.check_attributes_for_sql()
    name = get_full_name_for_sql(model)
    components = [f'CREATE TABLE {name} (']

    body: List[str] = []
    body.extend(indent(DefaultSQLRenderer.render(c), "  ") for c in model.columns)
    body.extend(indent(DefaultSQLRenderer.render(i), "  ") for i in model.indexes if i.pk)
    body.extend(indent(DefaultSQLRenderer.render(r), "  ") for r in get_inline_references_for_sql(model))

    if model._has_composite_pk():
        body.append(
            "  PRIMARY KEY ("
            + ', '.join(f'"{c.name}"' for c in model.columns if c.pk)
            + ')')
    components.append(',\n'.join(body))
    components.append(');')
    components.extend('\n' + DefaultSQLRenderer.render(i) for i in model.indexes if not i.pk)

    result = comment_to_sql(model.comment) if model.comment else ''
    result += '\n'.join(components)

    if model.note:
        result += f'\n\n{model.note.sql}'

    for col in model.columns:
        if col.note:
            quoted_note = f"'{col.note.prepare_text_for_sql()}'"
            note_sql = f'COMMENT ON COLUMN "{model.name}"."{col.name}" IS {quoted_note};'
            result += f'\n\n{note_sql}'
    return result
