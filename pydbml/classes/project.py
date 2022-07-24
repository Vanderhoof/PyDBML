from typing import Dict
from typing import Optional
from typing import Union

from .note import Note
from pydbml.tools import comment_to_dbml
from pydbml.tools import indent


class Project:
    def __init__(self,
                 name: str,
                 items: Optional[Dict[str, str]] = None,
                 note: Optional[Union['Note', str]] = None,
                 comment: Optional[str] = None):
        self.database = None
        self.name = name
        self.items = items
        self.note = Note(note)
        self.comment = comment

    def __repr__(self):
        """
        >>> Project('myproject')
        <Project 'myproject'>
        """

        return f'<Project {self.name!r}>'

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val: Note) -> None:
        self._note = val
        val.parent = self

    @property
    def dbml(self):
        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'Project "{self.name}" {{\n'
        if self.items:
            items_str = ''
            for k, v in self.items.items():
                if '\n' in v:
                    items_str += f"{k}: '''{v}'''\n"
                else:
                    items_str += f"{k}: '{v}'\n"
            result += indent(items_str[:-1]) + '\n'
        if self.note:
            result += indent(self.note.dbml) + '\n'
        result += '}'
        return result
