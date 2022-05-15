from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .base import SQLOjbect
from .column import Column
from .index import Index
from .note import Note
from .reference import Reference
from pydbml.constants import MANY_TO_ONE
from pydbml.constants import ONE_TO_MANY
from pydbml.constants import ONE_TO_ONE
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import IndexNotFoundError
from pydbml.exceptions import UnknownSchemaError
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import indent


if TYPE_CHECKING:  # pragma: no cover
    from pydbml.schema import Schema


class Table(SQLOjbect):
    '''Class representing table.'''

    required_attributes = ('name',)

    def __init__(self,
                 name: str,
                 alias: Optional[str] = None,
                 note: Optional[Union['Note', str]] = None,
                 header_color: Optional[str] = None,
                 # refs: Optional[List[TableReference]] = None,
                 comment: Optional[str] = None):
        self.schema: Optional[Schema] = None
        self.name = name
        self.columns: List[Column] = []
        self.indexes: List[Index] = []
        self.alias = alias if alias else None
        self.note = Note(note)
        self.header_color = header_color
        # self.refs = refs or []
        self.comment = comment

    def add_column(self, c: Column) -> None:
        '''
        Adds column to self.columns attribute and sets in this column the
        `table` attribute.
        '''
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

    def get_refs(self) -> List[Reference]:
        if not self.schema:
            raise UnknownSchemaError('Schema for the table is not set')
        return [ref for ref in self.schema.refs if ref.col1[0].table == self]

    def _get_references_for_sql(self) -> List[Reference]:
        '''
        return inline references for this table sql definition
        '''
        if not self.schema:
            raise UnknownSchemaError(f'Schema for the table {self} is not set')
        result = []
        for ref in self.schema.refs:
            if ref.inline:
                if (ref.type in (MANY_TO_ONE, ONE_TO_ONE)) and\
                        (ref.col1[0].table == self):
                    result.append(ref)
                elif (ref.type == ONE_TO_MANY) and (ref.col2[0].table == self):
                    result.append(ref)
        return result

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
        <Table 'customers'>
        '''

        return f'<Table {self.name!r}>'

    def __str__(self):
        '''
        >>> table = Table('customers')
        >>> table.add_column(Column('id', 'INTEGER'))
        >>> table.add_column(Column('name', 'VARCHAR2'))
        >>> print(table)
        customers(id, name)
        '''

        return f'{self.name}({", ".join(c.name for c in self.columns)})'

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
        components = [f'CREATE TABLE "{self.name}" (']
        body = []
        body.extend(indent(c.sql, 2) for c in self.columns)
        body.extend(indent(i.sql, 2) for i in self.indexes if i.pk)
        body.extend(indent(r.sql, 2) for r in self._get_references_for_sql())
        components.append(',\n'.join(body))
        components.append(');')
        components.extend('\n' + i.sql for i in self.indexes if not i.pk)

        result = comment_to_sql(self.comment) if self.comment else ''
        result += '\n'.join(components)

        if self.note:
            quoted_note = f"'{self.note.text}'"
            note_sql = f'COMMENT ON TABLE "{self.name}" IS {quoted_note};'
            result += f'\n\n{note_sql}'

        for col in self.columns:
            if col.note:
                quoted_note = f"'{col.note.text}'"
                note_sql = f'COMMENT ON COLUMN "{self.name}"."{col.name}" IS {quoted_note};'
                result += f'\n\n{note_sql}'
        return result

    @property
    def dbml(self):
        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'Table "{self.name}" '
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
