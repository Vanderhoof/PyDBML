from typing import Optional, Union

from .base import SQLObject, DBMLObject


class Note(SQLObject, DBMLObject):
    _eq_skip_fields = ('parent',)

    def __init__(self, text: Optional[Union[str, 'Note']] = None) -> None:
        self.text: str = str(text) if text is not None else ''
        self.parent: object = None

    def __str__(self):
        '''Note text'''
        return self.text

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        '''Note('Note text')'''
        return f'Note({repr(self.text)})'
