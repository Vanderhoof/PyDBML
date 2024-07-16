from typing import Any

from pydbml._classes.base import DBMLObject


class StickyNote(DBMLObject):
    dont_compare_fields = ('database',)

    def __init__(self, name: str, text: Any) -> None:
        self.name = name
        self.text = str(text) if text is not None else ''

        self.database = None

    def __str__(self):
        '''StickyNote('mynote', 'Note text')'''
        return self.__class__.__name__ + f'({repr(self.name)}, {repr(self.text)})'

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        '''<StickyNote 'mynote', 'Note text'>'''
        return f'<{self.__class__.__name__} {self.name!r}, {self.text!r}>'
