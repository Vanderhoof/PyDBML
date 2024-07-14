from itertools import chain
from textwrap import indent
from typing import List

from pydbml.classes import Reference, Column
from pydbml.exceptions import TableNotFoundError, DBMLError
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml
from .table import get_full_name_for_dbml


def validate_for_dbml(model: Reference):
    for col in chain(model.col1, model.col2):
        if col.table is None:
            raise TableNotFoundError(f'Table on {col} is not set')


def render_inline_reference(model: Reference) -> str:
    # settings are ignored for inline ref
    if len(model.col2) > 1:
        raise DBMLError('Cannot render DBML: composite ref cannot be inline')
    table_name = get_full_name_for_dbml(model.col2[0].table)
    return f'ref: {model.type} {table_name}."{model.col2[0].name}"'


def render_col(col: List[Column]) -> str:
    if len(col) == 1:
        return f'"{col[0].name}"'
    else:
        names = (f'"{c.name}"' for c in col)
        return f'({", ".join(names)})'


def render_options(model: Reference) -> str:
    options = []
    if model.on_update:
        options.append(f'update: {model.on_update}')
    if model.on_delete:
        options.append(f'delete: {model.on_delete}')
    if options:
        return f' [{", ".join(options)}]'
    return ''


def render_not_inline_reference(model: Reference) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += 'Ref'
    if model.name:
        result += f' {model.name}'

    result += (
        ' {\n    '  # type: ignore
        f'{get_full_name_for_dbml(model.table1)}.{render_col(model.col1)} '
        f'{model.type} '
        f'{get_full_name_for_dbml(model.table2)}.{render_col(model.col2)}'
        f'{render_options(model)}'
        '\n}'
    )
    return result


@DefaultDBMLRenderer.renderer_for(Reference)
def render_reference(model: Reference) -> str:
    validate_for_dbml(model)
    if model.inline:
        return render_inline_reference(model)
    else:
        return render_not_inline_reference(model)
