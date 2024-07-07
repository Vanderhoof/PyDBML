import re

from pydbml.classes import Note, Table, Column
from pydbml.renderer.sql.default.renderer import DefaultSQLRenderer


def prepare_text_for_sql(model: Note) -> str:
    '''
    - Process special escape sequence: slash before line break, which means no line break
      https://www.dbml.org/docs/#multi-line-string
    - replace all single quotes with double quotes
    '''

    pattern = re.compile(r'\\\n')
    result = pattern.sub('', model.text)

    result = result.replace("'", '"')
    return result


def generate_comment_on(model: Note, entity: str, name: str) -> str:
    """Generate a COMMENT ON clause out from this note."""
    quoted_text = f"'{prepare_text_for_sql(model)}'"
    note_sql = f'COMMENT ON {entity.upper()} "{name}" IS {quoted_text};'
    return note_sql


@DefaultSQLRenderer.renderer_for(Note)
def render_note(model: Note) -> str:
    """
    For Tables and Columns Note is converted into COMMENT ON clause. All other entities don't
    have notes generated in their SQL code, but as a fallback their notes are rendered as SQL
    comments when sql property is called directly.
    """

    if model.text:
        if isinstance(model.parent, (Table, Column)):
            return generate_comment_on(model, model.parent.__class__.__name__, model.parent.name)
        else:
            text = prepare_text_for_sql(model)
            return '\n'.join(f'-- {line}' for line in text.split('\n'))
    else:
        return ''
