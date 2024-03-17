import re
from typing import Any

from pydbml.tools import indent


class StickyNote:
    dont_compare_fields = ('database',)

    def __init__(self, name: str, text: Any) -> None:
        self.name = name
        self.text = str(text) if text is not None else ''

        self.database = None

    def __str__(self):
        '''
        >>> print(StickyNote('mynote', 'Note text'))
        StickyNote('mynote', 'Note text')
        '''

        return self.__class__.__name__ + f'({repr(self.name)}, {repr(self.text)})'

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        '''
        >>> StickyNote('mynote', 'Note text')
        <StickyNote 'mynote', 'Note text'>
        '''

        return f'<{self.__class__.__name__} {self.name!r}, {self.text!r}>'

    def _prepare_text_for_dbml(self):
        '''Escape single quotes'''
        pattern = re.compile(r"('''|')")
        return pattern.sub(r'\\\1', self.text)

    @property
    def dbml(self):
        text = self._prepare_text_for_dbml()
        if '\n' in text:
            note_text = f"'''\n{text}\n'''"
        else:
            note_text = f"'{text}'"

        note_text = indent(note_text)
        result = f'Note {self.name} {{\n{note_text}\n}}'
        return result
