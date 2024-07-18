from typing import Any

from .base import SQLObject, DBMLObject


class Note(SQLObject, DBMLObject):
    dont_compare_fields = ('parent',)

    def __init__(self, text: Any) -> None:
        self.text: str
        self.text = str(text) if text is not None else ''
        self.parent: Any = None

    def __str__(self):
        '''Note text'''
        return self.text

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        '''Note('Note text')'''
        return f'Note({repr(self.text)})'
