from typing import List
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .base import SQLObject
from .column import Column
from .expression import Expression
from .note import Note
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import note_option_to_dbml

if TYPE_CHECKING:  # pragma: no cover
    from .table import Table


class Index(SQLObject):
    '''Class representing index.'''
    required_attributes = ('subjects', 'table')

    def __init__(self,
                 subjects: List[Union[str, 'Column', 'Expression']],
                 name: Optional[str] = None,
                 unique: bool = False,
                 type: Optional[Literal['hash', 'btree']] = None,
                 pk: bool = False,
                 note: Optional[Union['Note', str]] = None,
                 comment: Optional[str] = None):
        self.subjects = subjects
        self.table: Optional['Table'] = None

        self.name = name if name else None
        self.unique = unique
        self.type = type
        self.pk = pk
        self.note = Note(note)
        self.comment = comment

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val: Note) -> None:
        self._note = val
        val.parent = self

    @property
    def subject_names(self):
        '''
        Returns updated list of subject names.
        '''
        return [s.name if isinstance(s, Column) else str(s) for s in self.subjects]

    def __repr__(self):
        '''
        >>> c = Column('col', 'int')
        >>> i = Index([c, '(c*2)'])
        >>> i
        <Index None, ['col', '(c*2)']>
        >>> from .table import Table
        >>> t = Table('test')
        >>> t.add_column(c)
        >>> t.add_index(i)
        >>> i
        <Index 'test', ['col', '(c*2)']>
        '''

        table_name = self.table.name if self.table else None
        return f"<Index {table_name!r}, {self.subject_names!r}>"

    def __str__(self):
        '''
        >>> c = Column('col', 'int')
        >>> i = Index([c, '(c*2)'])
        >>> print(i)
        Index([col, (c*2)])
        >>> from .table import Table
        >>> t = Table('test')
        >>> t.add_column(c)
        >>> t.add_index(i)
        >>> print(i)
        Index(test[col, (c*2)])
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
        subjects = []

        for subj in self.subjects:
            if isinstance(subj, Column):
                subjects.append(f'"{subj.name}"')
            elif isinstance(subj, Expression):
                subjects.append(subj.sql)
            else:
                subjects.append(subj)
        keys = ', '.join(subj for subj in subjects)
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
        subjects = []

        for subj in self.subjects:
            if isinstance(subj, Column):
                subjects.append(subj.name)
            elif isinstance(subj, Expression):
                subjects.append(subj.dbml)
            else:
                subjects.append(subj)

        result = comment_to_dbml(self.comment) if self.comment else ''

        if len(subjects) > 1:
            result += f'({", ".join(subj for subj in subjects)})'
        else:
            result += subjects[0]

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
