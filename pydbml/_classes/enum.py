from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from .base import SQLObject, DBMLObject
from .note import Note


class EnumItem(SQLObject, DBMLObject):
    '''Single enum item'''

    required_attributes = ('name',)

    def __init__(self,
                 name: str,
                 note: Optional[Union[Note, str]] = None,
                 comment: Optional[str] = None):
        self.name = name
        self.note = Note(note)
        self.comment = comment

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val: Note) -> None:
        self._note = val
        val.parent = self

    def __repr__(self):
        '''<EnumItem 'en-US'>'''
        return f'<EnumItem {self.name!r}>'

    def __str__(self):
        '''en-US'''
        return self.name


class Enum(SQLObject, DBMLObject):
    required_attributes = ('name', 'schema', 'items')

    def __init__(self,
                 name: str,
                 items: Iterable[Union['EnumItem', str]],
                 schema: str = 'public',
                 comment: Optional[str] = None):
        self.database = None
        self.name = name
        self.schema = schema
        self.comment = comment
        self.items: List[EnumItem] = []
        for item in items:
            self.add_item(item)

    def add_item(self, item: Union['EnumItem', str]) -> None:
        if isinstance(item, EnumItem):
            self.items.append(item)
        elif isinstance(item, str):
            self.items.append(EnumItem(item))

    def __getitem__(self, key: int) -> EnumItem:
        return self.items[key]

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        '''
        >>> en = EnumItem('en-US')
        >>> ru = EnumItem('ru-RU')
        >>> Enum('languages', [en, ru])
        <Enum 'languages', ['en-US', 'ru-RU']>
        '''

        item_names = [i.name for i in self.items]
        classname = self.__class__.__name__
        return f'<{classname} {self.name!r}, {item_names!r}>'

    def __str__(self):
        '''
        >>> en = EnumItem('en-US')
        >>> ru = EnumItem('ru-RU')
        >>> print(Enum('languages', [en, ru]))
        languages
        '''

        return self.name
