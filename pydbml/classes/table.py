from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union
from typing import Iterable

from .base import SQLObject
from .column import Column
from .index import Index
from .note import Note
from pydbml.constants import MANY_TO_ONE
from pydbml.constants import ONE_TO_MANY
from pydbml.constants import ONE_TO_ONE
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import IndexNotFoundError
from pydbml.exceptions import UnknownDatabaseError
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import indent


if TYPE_CHECKING:  # pragma: no cover
    from pydbml.database import Database
    from .reference import Reference


class Table(SQLObject):
    '''Class representing table.'''

    required_attributes = ('name', 'schema')

    def __init__(self,
                 name: str,
                 schema: str = 'public',
                 alias: Optional[str] = None,
                 columns: Optional[Iterable[Column]] = None,
                 indexes: Optional[Iterable[Index]] = None,
                 note: Optional[Union['Note', str]] = None,
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
            if isinstance(subject, Column) and subject.table != self:
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

    def get_references_for_sql(self) -> List['Reference']:
        """
        Return all references in the database where this table is on the left side of SQL
        reference definition.
        """
        if not self.database:
            raise UnknownDatabaseError(f'Database for the table {self} is not set')
        result = []
        for ref in self.database.refs:
            if (ref.type in (MANY_TO_ONE, ONE_TO_ONE)) and\
                    (ref.table1 == self):
                result.append(ref)
            elif (ref.type == ONE_TO_MANY) and (ref.table2 == self):
                result.append(ref)
        return result

    def _get_references_for_sql(self) -> List['Reference']:
        '''
        Return inline references for this table sql definition
        '''
        if self.abstract:
            return []
        return [r for r in self.get_references_for_sql() if r.inline]

    def _get_full_name_for_sql(self) -> str:
        if self.schema == 'public':
            return f'"{self.name}"'
        else:
            return f'"{self.schema}"."{self.name}"'

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

    @property
    def sql(self):
        '''
        Returns full SQL for table definition:

        CREATE TABLE "countries" (
          "code" int PRIMARY KEY,
          "name" varchar,
          "continent_name" varchar
        );

        Also returns indexes if they were defined:

        CREATE INDEX ON "products" ("id", "name");
        '''
        self.check_attributes_for_sql()
        name = self._get_full_name_for_sql()
        components = [f'CREATE TABLE {name} (']

        body = []
        body.extend(indent(c.sql, 2) for c in self.columns)
        body.extend(indent(i.sql, 2) for i in self.indexes if i.pk)
        body.extend(indent(r.sql, 2) for r in self._get_references_for_sql())

        if self._has_composite_pk():
            body.append(
                "  PRIMARY KEY ("
                + ', '.join(f'"{c.name}"' for c in self.columns if c.pk)
                + ')')
        components.append(',\n'.join(body))
        components.append(');')
        components.extend('\n' + i.sql for i in self.indexes if not i.pk)

        result = comment_to_sql(self.comment) if self.comment else ''
        result += '\n'.join(components)

        if self.note:
            result += f'\n\n{self.note.sql}'

        for col in self.columns:
            if col.note:
                quoted_note = f"'{col.note._prepare_text_for_sql()}'"
                note_sql = f'COMMENT ON COLUMN "{self.name}"."{col.name}" IS {quoted_note};'
                result += f'\n\n{note_sql}'
        return result

    @property
    def dbml(self):
        result = comment_to_dbml(self.comment) if self.comment else ''

        name = self._get_full_name_for_sql()

        result += f'Table {name} '
        if self.alias:
            result += f'as "{self.alias}" '
        result += '{\n'
        columns_str = '\n'.join(c.dbml for c in self.columns)
        result += indent(columns_str) + '\n'
        if self.note:
            result += indent(self.note.dbml) + '\n'
        if self.indexes:
            result += '\n    indexes {\n'
            indexes_str = '\n'.join(i.dbml for i in self.indexes)
            result += indent(indexes_str, 8) + '\n'
            result += '    }\n'

        result += '}'
        return result
