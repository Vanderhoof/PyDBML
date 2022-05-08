from typing import List
from typing import Optional
from typing import Union

from .base import SQLOjbect
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


class Enum(SQLOjbect):
    required_attributes = ('name', 'items')

    def __init__(self,
                 name: str,
                 items: List['EnumItem'],
                 comment: Optional[str] = None):
        self.schema = None
        self.name = name
        self.items = items
        self.comment = comment

    def __getitem__(self, key) -> EnumItem:
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
        result += f'CREATE TYPE "{self.name}" AS ENUM (\n'
        result += '\n'.join(f'{indent(i.sql, 2)}' for i in self.items)
        result += '\n);'
        return result

    @property
    def dbml(self):
        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'Enum "{self.name}" {{\n'
        items_str = '\n'.join(i.dbml for i in self.items)
        result += indent(items_str)
        result += '\n}'
        return result
