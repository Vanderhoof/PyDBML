import re
from typing import Any

from .base import SQLObject
from pydbml.tools import indent
from pydbml import classes


class Note(SQLObject):

    def __init__(self, text: Any):
        self.text: str
        if isinstance(text, Note):
            self.text = text.text
        else:
            self.text = str(text) if text else ''
        self.parent: Any = None

    def __str__(self):
        '''
        >>> print(Note('Note text'))
        Note text
        '''

        return self.text

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        '''
        >>> Note('Note text')
        Note('Note text')
        '''

        return f'Note({repr(self.text)})'

    def _prepare_text_for_sql(self) -> str:
        '''
        - Process special escape sequence: slash before line break, which means no line break
        https://www.dbml.org/docs/#multi-line-string

        - replace all single quotes with double quotes
        '''

        pattern = re.compile(r'\\\n')
        result = pattern.sub('', self.text)

        result = result.replace("'", '"')
        return result

    def _prepare_text_for_dbml(self):
        '''Escape single quotes'''
        pattern = re.compile(r"('''|')")
        return pattern.sub(r'\\\1', self.text)

    def generate_comment_on(self, entity: str, name: str) -> str:
        """Generate a COMMENT ON clause out from this note."""
        quoted_text = f"'{self._prepare_text_for_sql()}'"
        note_sql = f'COMMENT ON {entity.upper()} "{name}" IS {quoted_text};'
        return note_sql

    @property
    def sql(self):
        """
        For Tables and Columns Note is converted into COMMENT ON clause. All other entities don't
        have notes generated in their SQL code, but as a fallback their notes are rendered as SQL
        comments when sql property is called directly.
        """
        if self.text:
            if isinstance(self.parent, (classes.Table, classes.Column)):
                return self.generate_comment_on(self.parent.__class__.__name__, self.parent.name)
            else:
                text = self._prepare_text_for_sql()
                return '\n'.join(f'-- {line}' for line in text.split('\n'))
        else:
            return ''

    @property
    def dbml(self):
        text = self._prepare_text_for_dbml()
        if '\n' in text:
            note_text = f"'''\n{text}\n'''"
        else:
            note_text = f"'{text}'"

        note_text = indent(note_text)
        result = f'Note {{\n{note_text}\n}}'
        return result
