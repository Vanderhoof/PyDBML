from typing import Any

from .base import SQLObject
# from pydbml.tools import reformat_note_text
# from pydbml.tools import remove_indentation
from pydbml.tools import indent


class Note(SQLObject):
    def __init__(self, text: Any):
        self.text: str
        if isinstance(text, Note):
            self.text = text.text
        else:
            self.text = str(text) if text else ''

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

    @property
    def sql(self):
        if self.text:
            return '\n'.join(f'-- {line}' for line in self.text.split('\n'))
        else:
            return ''

    @property
    def dbml(self):
        if '\n' in self.text:
            note_text = f"'''\n{self.text}\n'''"
        else:
            note_text = f"'{self.text}'"

        note_text = indent(note_text)
        result = f'Note {{\n{note_text}\n}}'
        return result
