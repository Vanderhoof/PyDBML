from typing import Optional
from typing import Union
from typing import List

from .base import SQLOjbect
from .note import Note
from .column import Column
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import note_option_to_dbml


class Index(SQLOjbect):
    '''Class representing index.'''
    required_attributes = ('subjects', 'table')

    def __init__(self,
                 subjects: List[Union[str, 'Column']],
                 name: Optional[str] = None,
                 unique: bool = False,
                 type_: Optional[str] = None,
                 pk: bool = False,
                 note: Optional[Union['Note', str]] = None,
                 comment: Optional[str] = None):
        self.schema = None
        self.subjects = subjects
        self.table = None

        self.name = name if name else None
        self.unique = unique
        self.type = type_
        self.pk = pk
        self.note = Note(note)
        self.comment = comment

    @property
    def subject_names(self):
        '''
        For backward compatibility. Returns updated list of subject names.
        '''
        return [s.name if isinstance(s, Column) else s for s in self.subjects]

    def __repr__(self):
        '''
        >>> Index(['name', 'type'])
        <Index None, ['name', 'type']>
        >>> t = Table('t')
        >>> Index(['name', 'type'], table=t)
        <Index 't', ['name', 'type']>
        '''

        table_name = self.table.name if self.table else None
        return f"<Index {table_name!r}, {self.subject_names!r}>"

    def __str__(self):
        '''
        >>> print(Index(['name', 'type']))
        Index([name, type])
        >>> t = Table('t')
        >>> print(Index(['name', 'type'], table=t))
        Index(t[name, type])
        '''

        table_name = self.table.name if self.table else ''
        subjects = ', '.join(self.subject_names)
        return f"Index({table_name}[{subjects}])"

    @property
    def sql(self):
        '''
        Returns inline SQL of the index to be created separately from table
        definition:

        CREATE UNIQUE INDEX ON "products" USING HASH ("id");

        But if it's a (composite) primary key index, returns an inline SQL for
        composite primary key to be used inside table definition:

        PRIMARY KEY ("id", "name")

        '''
        self.check_attributes_for_sql()
        keys = ', '.join(f'"{key.name}"' if isinstance(key, Column) else key for key in self.subjects)
        if self.pk:
            result = comment_to_sql(self.comment) if self.comment else ''
            result += f'PRIMARY KEY ({keys})'
            return result

        components = ['CREATE']
        if self.unique:
            components.append('UNIQUE')
        components.append('INDEX')
        if self.name:
            components.append(f'"{self.name}"')
        components.append(f'ON "{self.table.name}"')
        if self.type:
            components.append(f'USING {self.type.upper()}')
        components.append(f'({keys})')
        result = comment_to_sql(self.comment) if self.comment else ''
        result += ' '.join(components) + ';'
        return result

    @property
    def dbml(self):
        def subject_to_str(val: str) -> str:
            if val.startswith('(') and val.endswith(')'):
                return f'`{val[1:-1]}`'
            else:
                return val

        result = comment_to_dbml(self.comment) if self.comment else ''

        subject_names = self.subject_names

        if len(subject_names) > 1:
            result += f'({", ".join(subject_to_str(sn) for sn in subject_names)})'
        else:
            result += subject_to_str(subject_names[0])

        options = []
        if self.name:
            options.append(f"name: '{self.name}'")
        if self.pk:
            options.append('pk')
        if self.unique:
            options.append('unique')
        if self.type:
            options.append(f'type: {self.type}')
        if self.note:
            options.append(note_option_to_dbml(self.note))

        if options:
            result += f' [{", ".join(options)}]'
        return result
