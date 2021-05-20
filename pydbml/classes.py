from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from .exceptions import AttributeMissingError
from .exceptions import ColumnNotFoundError
from .exceptions import DuplicateReferenceError


class SQLOjbect:
    '''
    Base class for all SQL objects.
    '''
    required_attributes: Tuple[str, ...] = ()

    def check_attributes_for_sql(self):
        '''
        Check if all attributes, required for rendering SQL are set in the
        instance. If some attribute is missing, raise AttributeMissingError
        '''
        for attr in self.required_attributes:
            if getattr(self, attr) is None:
                raise AttributeMissingError(
                    f'Cannot render SQL. Missing required attribute "{attr}".'
                )

    def __setattr__(self, name: str, value: Any):
        """
        Required for type testing with MyPy.
        """
        super().__setattr__(name, value)

    def __eq__(self, other: object) -> bool:
        """
        Two instances of the same SQLObject subclass are equal if all their
        attributes are equal.
        """

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False


class ReferenceBlueprint:
    '''
    Intermediate class for references during parsing. Table and columns are just
    strings at this point, as we can't check their validity until all schema
    is parsed.
    '''
    ONE_TO_MANY = '<'
    MANY_TO_ONE = '>'
    ONE_TO_ONE = '-'

    def __init__(self,
                 type_: str,
                 name: Optional[str] = None,
                 table1: Optional[str] = None,
                 col1: Optional[str] = None,
                 table2: Optional[str] = None,
                 col2: Optional[str] = None,
                 comment: Optional[str] = None,
                 on_update: Optional[str] = None,
                 on_delete: Optional[str] = None):
        self.type = type_
        self.name = name if name else None
        self.table1 = table1 if table1 else None
        self.col1 = col1 if col1 else None
        self.table2 = table2 if table2 else None
        self.col2 = col2 if col2 else None
        self.comment = comment
        self.on_update = on_update
        self.on_delete = on_delete

    def __repr__(self):
        components = [f"ReferenceBlueprint({self.type!r}"]
        if self.name:
            components.append(f'name={self.name!r}')
        if self.table1:
            components.append(f'table1={self.table1!r}')
        if self.col1:
            components.append(f'col1={self.col1!r}')
        if self.table2:
            components.append(f'table2={self.table2!r}')
        if self.col2:
            components.append(f'col2={self.col2!r}')
        if self.on_update:
            components.append(f'on_update={self.on_update!r}')
        if self.on_delete:
            components.append(f'on_delete={self.on_delete!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Reference("]
        if self.table1:
            components.append(self.table1)
        if self.col1:
            components.append(f'.{self.col1}')
        components.append(f' {self.type} ')
        if self.table2:
            components.append(self.table2)
        if self.col2:
            components.append(f'.{self.col2}')
        return ''.join(components) + ')'


class Reference(SQLOjbect):
    '''
    Class, representing a foreign key constraint.
    It is a separate object, which is not connected to Table or Column objects
    and its `sql` property contains the ALTER TABLE clause.
    '''
    required_attributes = ('type', 'table1', 'col1', 'table2', 'col2')

    ONE_TO_MANY = '<'
    MANY_TO_ONE = '>'
    ONE_TO_ONE = '-'

    def __init__(self,
                 type_: str,
                 table1: Table,
                 col1: Union[Column, List[Column]],
                 table2: Table,
                 col2: Union[Column, List[Column]],
                 name: Optional[str] = None,
                 comment: Optional[str] = None,
                 on_update: Optional[str] = None,
                 on_delete: Optional[str] = None):
        self.type = type_
        self.table1 = table1
        self.col1 = [col1] if isinstance(col1, Column) else list(col1)
        self.table2 = table2
        self.col2 = [col2] if isinstance(col2, Column) else list(col2)
        self.name = name if name else None
        self.comment = comment
        self.on_update = on_update
        self.on_delete = on_delete

    def __repr__(self):
        components = [
            f"Reference({self.type!r}",
            f"{self.table1!r}",
            f"{self.col1!r}",
            f"{self.table2!r}",
            f"{self.col2!r}",
        ]
        if self.name:
            components.append(f'name={self.name!r}')
        if self.on_update:
            components.append(f'on_update={self.on_update!r}')
        if self.on_delete:
            components.append(f'on_delete={self.on_delete!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Reference("]
        if self.table1:
            components.append(self.table1.name)
        if self.col1:
            components.append(f'[{", ".join(c.name for c in self.col1)}]')
        components.append(f' {self.type} ')
        if self.table2:
            components.append(self.table2.name)
        if self.col2:
            components.append(f'[{", ".join(c.name for c in self.col2)}]')
        return ''.join(components) + ')'

    @property
    def sql(self):
        '''
        Returns SQL of the reference:

        ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers ("id");

        '''
        self.check_attributes_for_sql()
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''

        if self.type in (self.MANY_TO_ONE, self.ONE_TO_ONE):
            t1 = self.table1
            c1 = ', '.join(self.col1)
            t2 = self.table2
            c2 = ', '.join(self.col2)
        else:
            t1 = self.table2
            c1 = ', '.join(self.col2)
            t2 = self.table1
            c2 = ', '.join(self.col1)

        result = (
            f'ALTER TABLE "{t1.name}" ADD {c}FOREIGN KEY ("{c1.name}") '
            f'REFERENCES "{t2.name} ("{c2.name}")'
        )
        if self.on_update:
            result += f' ON UPDATE {self.on_update.upper()}'
        if self.on_delete:
            result += f' ON DELETE {self.on_delete.upper()}'
        return result + ';'


class TableReference(SQLOjbect):
    '''
    Class, representing a foreign key constraint.
    This object should be assigned to the `refs` attribute of a Table object.
    Its `sql` property contains the inline definition of the FOREIGN KEY clause.
    '''
    required_attributes = ('col', 'ref_table', 'ref_col')

    def __init__(self,
                 col: Union[Column, List[Column]],
                 ref_table: Table,
                 ref_col: Union[Column, List[Column]],
                 name: Optional[str] = None,
                 on_delete: Optional[str] = None,
                 on_update: Optional[str] = None):
        self.col = [col] if isinstance(col, Column) else list(col)
        self.ref_table = ref_table
        self.ref_col = [ref_col] if isinstance(ref_col, Column) else list(ref_col)
        self.name = name
        self.on_update = on_update
        self.on_delete = on_delete

    def __repr__(self):
        components = [f"TableReference({self.col!r}, {self.ref_table!r}, {self.ref_col!r}"]
        if self.name:
            components.append(f'name={self.name!r}')
        if self.on_update:
            components.append(f'on_update={self.on_update!r}')
        if self.on_delete:
            components.append(f'on_delete={self.on_delete!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        cols = '", "'.join(c.name for c in self.col)
        ref_cols = '", "'.join(c.name for c in self.ref_col)
        return f"TableReference({cols} -> {self.ref_table.name}[{ref_cols}])"

    @property
    def sql(self):
        '''
        Returns inline SQL of the reference, which should be a part of table definition:

        FOREIGN KEY ("order_id") REFERENCES "orders ("id")

        '''
        self.check_attributes_for_sql()
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''
        cols = '", "'.join(c.name for c in self.col)
        ref_cols = '", "'.join(c.name for c in self.ref_col)
        result = (
            f'{c}FOREIGN KEY ("{cols}") '
            f'REFERENCES "{self.ref_table.name} ("{ref_cols}")'
        )
        if self.on_update:
            result += f' ON UPDATE {self.on_update.upper()}'
        if self.on_delete:
            result += f' ON DELETE {self.on_delete.upper()}'
        return result


class Note:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        return f'Note({repr(self.text)})'

    @property
    def sql(self):
        if self.text:
            return '\n'.join(f'-- {line}' for line in self.text.split('\n'))
        else:
            return ''


class Column(SQLOjbect):
    '''Class representing table column.'''

    required_attributes = ('name', 'type')

    def __init__(self,
                 name: str,
                 type_: str,
                 unique: bool = False,
                 not_null: bool = False,
                 pk: bool = False,
                 autoinc: bool = False,
                 default: Optional[Union[str, int, bool, float]] = None,
                 note: Optional[Note] = None,
                 ref_blueprints: Optional[List[ReferenceBlueprint]] = None,
                 comment: Optional[str] = None):
        self.name = name
        self.type = type_
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.autoinc = autoinc
        self.comment = comment

        self.default = default

        self.note = note or Note('')
        self.ref_blueprints = ref_blueprints or []
        for ref in self.ref_blueprints:
            ref.col1 = self.name

        self._table: Optional[Table] = None

    @property
    def table(self) -> Optional[Table]:
        return self._table

    @table.setter
    def table(self, v: Table):
        self._table = v
        for ref in self.ref_blueprints:
            ref.table1 = v.name

    @property
    def sql(self):
        '''
        Returns inline SQL of the column, which should be a part of table definition:

        "id" integer PRIMARY KEY AUTOINCREMENT

        '''
        self.check_attributes_for_sql()
        components = [f'"{self.name}"', str(self.type)]
        if self.pk:
            components.append('PRIMARY KEY')
        if self.autoinc:
            components.append('AUTOINCREMENT')
        if self.unique:
            components.append('UNIQUE')
        if self.not_null:
            components.append('NOT NULL')
        if self.default is not None:
            components.append('DEFAULT ' + str(self.default))
        if self.note:
            components.append(self.note.sql)
        return ' '.join(components)

    def __repr__(self):
        components = [f"Column({self.name!r}, {self.type!r}"]
        if self.unique:
            components.append(f'unique=True')
        if self.not_null:
            components.append(f'not_null=True')
        if self.pk:
            components.append(f'pk=True')
        if self.autoinc:
            components.append(f'autoinc=True')
        if self.default:
            components.append(f'default={self.default!r}')
        if self.note:
            components.append(f'note={self.note!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Column({self.name} {self.type}"]
        if self.unique:
            components.append(f'unique')
        if self.not_null:
            components.append(f'not_null')
        if self.pk:
            components.append(f'pk')
        if self.autoinc:
            components.append(f'autoincrement')
        if self.default:
            components.append(f'default={self.default!r}')
        return ' '.join(components) + ')'


class Index(SQLOjbect):
    '''Class representing index.'''
    required_attributes = ('subjects', 'table')

    def __init__(self,
                 subject_names: List[str],
                 name: Optional[str] = None,
                 table: Optional[Table] = None,
                 unique: bool = False,
                 type_: Optional[str] = None,
                 pk: bool = False,
                 note: Optional[Note] = None,
                 comment: Optional[str] = None):
        self.subject_names = subject_names
        self.subjects: List[Union[Column, str]] = []

        self.name = name if name else None
        self.table = table
        self.unique = unique
        self.type = type_
        self.pk = pk
        self.note = note or Note('')
        self.comment = comment

    def __repr__(self):
        components = [f"Index({self.subject_names!r}"]
        if self.name:
            components.append(f'name={self.name!r}')
        if self.unique:
            components.append(f'unique=True')
        if self.type:
            components.append(f'type_={self.type!r}')
        if self.pk:
            components.append(f'pk=True')
        if self.note:
            components.append(f'note_={self.note!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Index("]
        if len(self.subjects) == 1:
            components[0] += self.subjects[0]
        else:
            components[0] += '(' + ', '.join(self.subjects) + ')'
        if self.name:
            components.append(f'{self.name!r}')
        if self.unique:
            components.append(f'unique')
        if self.type:
            components.append(f'{self.type}')
        if self.pk:
            components.append(f'pk')
        return ' '.join(components) + ')'

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
            return f'PRIMARY KEY ({keys})'

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
        result = ' '.join(components) + ';'
        if self.note:
            result += f' {self.note.sql}'
        return result


class Table(SQLOjbect):
    '''Class representing table.'''

    required_attributes = ('name',)

    def __init__(self,
                 name: str,
                 alias: Optional[str] = None,
                 note: Optional[Note] = None,
                 header_color: Optional[str] = None,
                 refs: Optional[List[TableReference]] = None,
                 comment: Optional[str] = None):
        self.name = name
        self.columns: List[Column] = []
        self.indexes: List[Index] = []
        self.column_dict: Dict[str, Column] = {}
        self.alias = alias if alias else None
        self.note = note or Note('')
        self.header_color = header_color
        self.refs = refs or []
        self.comment = comment

    def add_column(self, c: Column) -> None:
        '''
        Adds column to self.columns attribute and sets in this column the
        `table` attribute.
        '''
        c.table = self
        self.columns.append(c)
        self.column_dict[c.name] = c

    def add_index(self, i: Index) -> None:
        '''
        Adds index to self.indexes attribute and sets in this index the
        `table` attribute.
        '''
        for subj in i.subject_names:
            if subj.startswith('(') and subj.endswith(')'):
                # subject is an expression, add it as string
                i.subjects.append(subj)
            else:
                try:
                    col = self[subj]
                    i.subjects.append(col)
                except KeyError:
                    raise ColumnNotFoundError(f'Cannot add index, column "{subj}" not defined in table "{self.name}".')

        i.table = self
        self.indexes.append(i)

    def add_ref(self, r: TableReference) -> None:
        '''
        Adds a reference to the table. If reference already present in the table,
        raises DuplicateReferenceError.
        '''
        if r in self.refs:
            raise DuplicateReferenceError(f'Reference with same endpoints {r} already present in the table.')
        self.refs.append(r)

    def __getitem__(self, k: Union[int, str]) -> Column:
        if isinstance(k, int):
            return self.columns[k]
        else:
            return self.column_dict[k]

    def get(self, k, default=None):
        return self.column_dict.get(k, default)

    def __iter__(self):
        return iter(self.columns)

    def __repr__(self):
        components = [f"Table({self.name!r}, {self.columns!r}"]
        if self.alias:
            components.append(f'alias={self.alias!r}')
        if self.indexes:
            components.append(f'indexes={self.indexes!r}')
        if self.note:
            components.append(f'note={self.note!r}')
        if self.header_color:
            components.append(f'header_color={self.header_color!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Table {self.name}"]
        if self.alias:
            components.append(f' as {self.alias} ')
        components.append('(' + ', '.join(c.name for c in self.columns))
        return ''.join(components) + ')'

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
        if self.note:
            components.append(f'  {self.note.sql}')
        body = []
        body.extend('  ' + c.sql for c in self.columns)
        body.extend('  ' + i.sql for i in self.indexes if i.pk)
        body.extend('  ' + r.sql for r in self.refs)
        components.append(',\n'.join(body))
        components.append(');\n')
        components.extend(i.sql + '\n' for i in self.indexes if not i.pk)
        return '\n'.join(components)


class EnumItem:
    '''Single enum item. Does not translate into SQL'''

    def __init__(self,
                 name: str,
                 note: Optional[Note] = None,
                 comment: Optional[str] = None):
        self.name = name
        self.note = note or Note('')
        self.comment = comment

    def __repr__(self):
        components = [f'EnumItem({self.name!r}']
        if self.note:
            components.append(f'note={self.note!r}')
        return ', '.join(components) + ')'

    def __str__(self):
        return self.name

    @property
    def sql(self):
        components = [f"'{self.name}',"]
        if self.note:
            components.append(self.note.sql)
        return ' '.join(components)


class Enum(SQLOjbect):
    required_attributes = ('name', 'items')

    def __init__(self,
                 name: str,
                 items: List[EnumItem],
                 comment: Optional[str] = None):
        self.name = name
        self.items = items
        self.comment = comment

    def get_type(self):
        return EnumType(self.name, self.items)

    def __getitem__(self, key) -> EnumItem:
        return self.items[key]

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return f'Enum({self.name!r}, {self.items!r})'

    def __str__(self):
        return (
            f'Enum {self.name} (' + ', '.join(str(i) for i in self.items) + ')'
        )

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
        return f'CREATE TYPE "{self.name}" AS ENUM (\n' +\
               '\n'.join(f'  {i.sql}' for i in self.items) +\
               '\n);'


class EnumType(Enum):
    '''
    Enum object, intended to be put in the `type` attribute of a column.
    '''

    def __repr__(self):
        return f'EnumType({self.name!r}, {self.items!r})'

    def __str__(self):
        return self.name


class TableGroup:
    '''
    TableGroup `items` parameter initially holds just the names of the tables,
    but after parsing the whole document, PyDBMLParseResults class replaces
    them with references to actual tables.
    '''

    def __init__(self,
                 name: str,
                 items: Union[List[str], List[Table]],
                 comment: Optional[str] = None):
        self.name = name
        self.items = items
        self.comment = comment

    def __repr__(self):
        return f'TableGroup({self.name!r}, {self.items!r})'

    def __getitem__(self, key) -> str:
        return self.items[key]

    def __iter__(self):
        return iter(self.items)


class Project:
    def __init__(self,
                 name: str,
                 items: Optional[Dict[str, str]] = None,
                 note: Optional[Note] = None,
                 comment: Optional[str] = None):
        self.name = name
        self.items = items
        self.note = note or Note('')
        self.comment = comment

    def __repr__(self):
        components = [f'Project({self.name!r}']
        if self.items:
            components.append(f'items={self.items!r}')
        if self.note:
            components.append(f'note={self.note!r}')
        return ', '.join(components) + ')'
