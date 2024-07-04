from itertools import chain
from textwrap import indent

from pydbml.classes import Reference
from pydbml.exceptions import TableNotFoundError, DBMLError
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml
from .table import get_full_name_for_dbml


def validate_for_dbml(model: Reference):
    for col in chain(model.col1, model.col2):
        if col.table is None:
            raise TableNotFoundError(f'Table on {col} is not set')


@DefaultDBMLRenderer.renderer_for(Reference)
def render_reference(model: Reference) -> str:
    validate_for_dbml(model)
    if model.inline:
        # settings are ignored for inline ref
        if len(model.col2) > 1:
            raise DBMLError('Cannot render DBML: composite ref cannot be inline')
        table_name = get_full_name_for_dbml(model.col2[0].table)
        return f'ref: {model.type} {table_name}."{model.col2[0].name}"'
    else:
        result = comment_to_dbml(model.comment) if model.comment else ''
        result += 'Ref'
        if model.name:
            result += f' {model.name}'

        if len(model.col1) == 1:
            col1 = f'"{model.col1[0].name}"'
        else:
            names = (f'"{c.name}"' for c in model.col1)
            col1 = f'({", ".join(names)})'

        if len(model.col2) == 1:
            col2 = f'"{model.col2[0].name}"'
        else:
            names = (f'"{c.name}"' for c in model.col2)
            col2 = f'({", ".join(names)})'

        options = []
        if model.on_update:
            options.append(f'update: {model.on_update}')
        if model.on_delete:
            options.append(f'delete: {model.on_delete}')

        options_str = f' [{", ".join(options)}]' if options else ''
        result += (
            ' {\n    '  # type: ignore
            f'{get_full_name_for_dbml(model.table1)}.{col1} '
            f'{model.type} '
            f'{get_full_name_for_dbml(model.table2)}.{col2}'
            f'{options_str}'
            '\n}'
        )
        return result
