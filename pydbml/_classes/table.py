from typing import Iterable
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import IndexNotFoundError
from pydbml.exceptions import UnknownDatabaseError
from .base import SQLObject, DBMLObject
from .column import Column
from .index import Index
from .note import Note

if TYPE_CHECKING:  # pragma: no cover
    from pydbml.database import Database
    from .reference import Reference


class Table(SQLObject, DBMLObject):
    '''Class representing table.'''

    required_attributes = ('name', 'schema')
    dont_compare_fields = ('database',)

    def __init__(self,
                 name: str,
                 schema: str = 'public',
                 alias: Optional[str] = None,
                 columns: Optional[Iterable[Column]] = None,
                 indexes: Optional[Iterable[Index]] = None,
                 note: Optional[Union[Note, str]] = None,
                 header_color: Optional[str] = None,
                 comment: Optional[str] = None,
                 abstract: bool = False):
        self.database: Optional[Database] = None
        self.name = name
        self.schema = schema
        self.columns: List[Column] = []
        for column in columns or []:
            self.add_column(column)
        self.indexes: List[Index] = []
        for index in indexes or []:
            self.add_index(index)
        self.alias = alias if alias else None
        self.note = Note(note)
        self.header_color = header_color
        self.comment = comment
        self.abstract = abstract

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val: Note) -> None:
        self._note = val
        val.parent = self

    @property
    def full_name(self) -> str:
        return f'{self.schema}.{self.name}'

    def _has_composite_pk(self) -> bool:
        return sum(c.pk for c in self.columns) > 1

    def add_column(self, c: Column) -> None:
        '''
        Adds column to self.columns attribute and sets in this column the
        `table` attribute.
        '''
        if not isinstance(c, Column):
            raise TypeError('Columns must be of type Column')
        c.table = self
        self.columns.append(c)

    def delete_column(self, c: Union[Column, int]) -> Column:
        if isinstance(c, Column):
            if c in self.columns:
                c.table = None
                return self.columns.pop(self.columns.index(c))
            else:
                raise ColumnNotFoundError(f'Column {c} if missing in the table')
        elif isinstance(c, int):
            self.columns[c].table = None
            return self.columns.pop(c)

    def add_index(self, i: Index) -> None:
        '''
        Adds index to self.indexes attribute and sets in this index the
        `table` attribute.
        '''
        if not isinstance(i, Index):
            raise TypeError('Indexes must be of type Index')
        for subject in i.subjects:
            if isinstance(subject, Column) and subject.table is not self:
                raise ColumnNotFoundError(f'Column {subject} not in the table')
        i.table = self
        self.indexes.append(i)

    def delete_index(self, i: Union[Index, int]) -> Index:
        if isinstance(i, Index):
            if i in self.indexes:
                i.table = None
                return self.indexes.pop(self.indexes.index(i))
            else:
                raise IndexNotFoundError(f'Index {i} if missing in the table')
        elif isinstance(i, int):
            self.indexes[i].table = None
            return self.indexes.pop(i)

    def get_refs(self) -> List['Reference']:
        if not self.database:
            raise UnknownDatabaseError('Database for the table is not set')
        return [ref for ref in self.database.refs if ref.table1 == self]

    def __getitem__(self, k: Union[int, str]) -> Column:
        if isinstance(k, int):
            return self.columns[k]
        elif isinstance(k, str):
            for c in self.columns:
                if c.name == k:
                    return c
            raise ColumnNotFoundError(f'Column {k} not present in table {self.name}')
        else:
            raise TypeError('indeces must be str or int')

    def get(self, k, default: Optional[Column] = None) -> Optional[Column]:
        try:
            return self.__getitem__(k)
        except (IndexError, ColumnNotFoundError):
            return default

    def __iter__(self):
        return iter(self.columns)

    def __repr__(self):
        '''
        >>> table = Table('customers')
        >>> table
        <Table 'public' 'customers'>
        '''

        return f'<Table {self.schema!r} {self.name!r}>'

    def __str__(self):
        '''
        >>> table = Table('customers')
        >>> table.add_column(Column('id', 'INTEGER'))
        >>> table.add_column(Column('name', 'VARCHAR2'))
        >>> print(table)
        public.customers(id, name)
        '''

        return f'{self.schema}.{self.name}({", ".join(c.name for c in self.columns)})'
