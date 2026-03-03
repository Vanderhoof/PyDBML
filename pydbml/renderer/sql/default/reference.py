from itertools import chain
from typing import List

from pydbml.classes import Reference, Column
from pydbml.constants import MANY_TO_MANY, MANY_TO_ONE, ONE_TO_ONE, ONE_TO_MANY
from pydbml.exceptions import TableNotFoundError
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer
from pydbml.renderer.sql.default.utils import comment_to_sql, get_full_name_for_sql


def col_names(cols: List[Column]) -> str:
    return ', '.join(f'"{c.name}"' for c in cols)


def validate_for_sql(model: Reference) -> None:
    for col in chain(model.col1, model.col2):
        if col.table is None:
            raise TableNotFoundError(f'Table for column {col!r} is not set')


def generate_inline_sql(
    model: Reference,
    source_col: List[Column],
    ref_col: List[Column],
    constraint: str = '',
) -> str:
    constraint = (constraint.strip() + ' ') if constraint else ''
    result = comment_to_sql(model.comment) if model.comment else ''
    ref_table = get_full_name_for_sql(ref_col[0].table)  # type: ignore[arg-type]
    result += f'{constraint}FOREIGN KEY ({col_names(source_col)}) REFERENCES {ref_table} ({col_names(ref_col)})'
    if model.on_update:
        result += f' ON UPDATE {model.on_update.upper()}'
    if model.on_delete:
        result += f' ON DELETE {model.on_delete.upper()}'
    return result


def generate_not_inline_sql(
    model: Reference,
    source_col: List[Column],
    ref_col: List[Column],
    constraint: str = '',
) -> str:
    constraint = (constraint.strip() + ' ') if constraint else ''
    result = comment_to_sql(model.comment) if model.comment else ''
    source_table = get_full_name_for_sql(source_col[0].table)  # type: ignore[arg-type]
    ref_table = get_full_name_for_sql(ref_col[0].table)  # type: ignore[arg-type]
    result += (
        f'ALTER TABLE {source_table}'
        f' ADD {constraint}FOREIGN KEY ({col_names(source_col)})'
        f' REFERENCES {ref_table} ({col_names(ref_col)})'
    )
    if model.on_update:
        result += f' ON UPDATE {model.on_update.upper()}'
    if model.on_delete:
        result += f' ON DELETE {model.on_delete.upper()}'
    return result + ';'


def generate_many_to_many_sql(model: Reference) -> str:
    join_table = model.join_table
    table_sql = join_table.sql  # type: ignore[union-attr]

    n = len(model.col1)
    ref1_sql = generate_not_inline_sql(model, join_table.columns[:n], model.col1)  # type: ignore[union-attr]
    ref2_sql = generate_not_inline_sql(model, join_table.columns[n:], model.col2)  # type: ignore[union-attr]

    return '\n\n'.join((table_sql, ref1_sql, ref2_sql))


@DefaultSQLRenderer.renderer_for(Reference)
def render_reference(model: Reference) -> str:
    '''
    Returns SQL of the reference:

    ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("id");
    '''
    validate_for_sql(model)

    if model.type == MANY_TO_MANY:
        return generate_many_to_many_sql(model)

    constraint = f'CONSTRAINT "{model.name}"' if model.name else ''
    func = generate_inline_sql if model.inline else generate_not_inline_sql
    if model.type in (MANY_TO_ONE, ONE_TO_ONE):
        return func(model=model, source_col=model.col1, ref_col=model.col2, constraint=constraint)
    elif model.type == ONE_TO_MANY:
        return func(model=model, source_col=model.col2, ref_col=model.col1, constraint=constraint)
    return ''
