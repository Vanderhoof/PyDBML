from typing import List, Dict, Union

from pydbml.classes import Column, Enum, Reference, Table
from pydbml.constants import MANY_TO_ONE, ONE_TO_MANY
from pydbml.tools import comment


def comment_to_sql(val: str) -> str:
    return comment(val, '--')


def reorder_tables_for_sql(tables: List['Table'], refs: List['Reference']) -> List['Table']:
    """
    Attempt to reorder the tables, so that they are defined in SQL before they are referenced by
    inline foreign keys.

    Won't aid the rare cases of cross-references and many-to-many relations.
    """

    references: Dict[str, int] = {}
    for ref in refs:
        if ref.inline:
            if ref.type == MANY_TO_ONE and ref.table1 is not None:
                table_name = ref.table1.name
            elif ref.type == ONE_TO_MANY and ref.table2 is not None:
                table_name = ref.table2.name
            else:
                continue
            references[table_name] = references.get(table_name, 0) + 1
    return sorted(tables, key=lambda t: references.get(t.name, 0), reverse=True)


def get_full_name_for_sql(model: Union[Table, Enum]) -> str:
    if model.schema == 'public':
        return f'"{model.name}"'
    else:
        return f'"{model.schema}"."{model.name}"'
