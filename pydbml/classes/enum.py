from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from .base import SQLObject
from .note import Note
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import indent
from pydbml.tools import note_option_to_dbml


class EnumItem:
    '''Single enum item'''

    def __init__(self,
                 name: str,
                 note: Optional[Union['Note', str]] = None,
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
        '''
        >>> EnumItem('en-US')
        <EnumItem 'en-US'>
        '''

        return f'<EnumItem {self.name!r}>'

    def __str__(self):
        '''
        >>> print(EnumItem('en-US'))
        en-US
        '''

        return self.name

    @property
    def sql(self):
        result = comment_to_sql(self.comment) if self.comment else ''
        result += f"'{self.name}',"
        return result

    @property
    def dbml(self):
        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'"{self.name}"'
        if self.note:
            result += f' [{note_option_to_dbml(self.note)}]'
        return result


class Enum(SQLObject):
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

    def _get_full_name_for_sql(self) -> str:
        if self.schema == 'public':
            return f'"{self.name}"'
        else:
            return f'"{self.schema}"."{self.name}"'

    @property
    def sql(self):
        '''
        Returns SQL for enum type:

        CREATE TYPE "job_status" AS ENUM (
          'created',
          'running',
          'donef',
          'failure',
        );

        '''
        self.check_attributes_for_sql()
        result = comment_to_sql(self.comment) if self.comment else ''
        result += f'CREATE TYPE {self._get_full_name_for_sql()} AS ENUM (\n'
        result += '\n'.join(f'{indent(i.sql, 2)}' for i in self.items)
        result += '\n);'
        return result

    @property
    def dbml(self):
        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'Enum {self._get_full_name_for_sql()} {{\n'
        items_str = '\n'.join(i.dbml for i in self.items)
        result += indent(items_str)
        result += '\n}'
        return result
