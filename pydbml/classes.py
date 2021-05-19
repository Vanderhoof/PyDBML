from __future__ import annotations
from typing import Optional, Tuple, Union, List, Dict

from .exceptions import AttributeMissingError, ColumnNotFoundError


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
        components = [f"ReferenceBlueprint({repr(self.type)}"]
        if self.name:
            components.append(f'name={repr(self.name)}')
        if self.table1:
            components.append(f'table1={repr(self.table1)}')
        if self.col1:
            components.append(f'col1={repr(self.col1)}')
        if self.table2:
            components.append(f'table2={repr(self.table2)}')
        if self.col2:
            components.append(f'col2={repr(self.col2)}')
        if self.on_update:
            components.append(f'on_update={repr(self.on_update)}')
        if self.on_delete:
            components.append(f'on_delete={repr(self.on_delete)}')
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
                 col1: Column,
                 table2: Table,
                 col2: Column,
                 name: Optional[str] = None,
                 comment: Optional[str] = None,
                 on_update: Optional[str] = None,
                 on_delete: Optional[str] = None):
        self.type = type_
        self.table1 = table1
        self.col1 = col1
        self.table2 = table2
        self.col2 = col2
        self.name = name if name else None
        self.comment = comment
        self.on_update = on_update
        self.on_delete = on_delete

    def __repr__(self):
        components = [
            f"Reference({repr(self.type)}",
            f"{repr(self.table1)}",
            f"{repr(self.col1)}",
            f"{repr(self.table2)}",
            f"{repr(self.col2)}",
        ]
        if self.name:
            components.append(f'name={repr(self.name)}')
        if self.on_update:
            components.append(f'on_update={repr(self.on_update)}')
        if self.on_delete:
            components.append(f'on_delete={repr(self.on_delete)}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Reference("]
        if self.table1:
            components.append(self.table1.name)
        if self.col1:
            components.append(f'.{self.col1.name}')
        components.append(f' {self.type} ')
        if self.table2:
            components.append(self.table2.name)
        if self.col2:
            components.append(f'.{self.col2.name}')
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
            c1 = self.col1
            t2 = self.table2
            c2 = self.col2
        else:
            t1 = self.table2
            c1 = self.col2
            t2 = self.table1
            c2 = self.col1

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
                 col: Column,
                 ref_table: Table,
                 ref_col: Column,
                 name: Optional[str] = None,
                 on_delete: Optional[str] = None,
                 on_update: Optional[str] = None):
        self.col = col
        self.ref_table = ref_table
        self.ref_col = ref_col
        self.name = name
        self.on_update = on_update
        self.on_delete = on_delete

    def __repr__(self):
        components = [f"TableReference({repr(self.col)}, {repr(self.ref_table)}, {repr(self.ref_col)}"]
        if self.name:
            components.append(f'name={repr(self.name)}')
        if self.on_update:
            components.append(f'on_update={repr(self.on_update)}')
        if self.on_delete:
            components.append(f'on_delete={repr(self.on_delete)}')
        return ', '.join(components) + ')'

    def __str__(self):
        return f"TableReference({self.col.name} -> {self.ref_table.name}.{self.ref_col.name})"

    @property
    def sql(self):
        '''
        Returns inline SQL of the reference, which should be a part of table definition:

        FOREIGN KEY ("order_id") REFERENCES "orders ("id")

        '''
        self.check_attributes_for_sql()
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''
        result = (
            f'{c}FOREIGN KEY ("{self.col.name}") '
            f'REFERENCES "{self.ref_table.name} ("{self.ref_col.name}")'
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
            return '\n'.join(f'-- {l}' for l in self.text.split('\n'))
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
                 default: Optional[str] = None,
                 note: Optional[str] = None,
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
        components = [f"Column({repr(self.name)}, {repr(self.type)}"]
        if self.unique:
            components.append(f'unique=True')
        if self.not_null:
            components.append(f'not_null=True')
        if self.pk:
            components.append(f'pk=True')
        if self.autoinc:
            components.append(f'autoinc=True')
        if self.default:
            components.append(f'default={repr(self.default)}')
        if self.note:
            components.append(f'note={repr(self.note)}')
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
            components.append(f'default={repr(self.default)}')
        return ' '.join(components) + ')'


class Index(SQLOjbect):
    '''Class representing index.'''
    required_attributes = ('subjects',)

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
        self.subjects: List[str] = []

        self.name = name if name else None
        self.table = table
        self.unique = unique
        self.type = type_
        self.pk = pk
        self.note = note or Note('')
        self.comment = comment

    def __repr__(self):
        components = [f"Index({repr(self.subject_names)}"]
        if self.name:
            components.append(f'name={repr(self.name)}')
        if self.unique:
            components.append(f'unique=True')
        if self.type:
            components.append(f'type_={repr(self.type)}')
        if self.pk:
            components.append(f'pk=True')
        if self.note:
            components.append(f'note_={repr(self.note)}')
        return ', '.join(components) + ')'

    def __str__(self):
        components = [f"Index("]
        if len(self.subjects) == 1:
            components[0] += self.subjects[0]
        else:
            components[0] += '(' + ', '.join(self.subjects) + ')'
        if self.name:
            components.append(f'{repr(self.name)}')
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
        keys = ', '.join(f'"{key.name}"' for key in self.subjects)
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
                 refs: Optional[List[Reference]] = None,
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

    def add_column(self, c: Column):
        '''
        Adds column to self.columns attribute and sets in this column the
        `table` attribute.
        '''
        c.table = self
        self.columns.append(c)
        self.column_dict[c.name] = c

    def add_index(self, i: Index):
        '''
        Adds index to self.indexes attribute and sets in this index the
        `table` attribute.
        '''
        for subj in i.subject_names:
            col = self.get(subj)
            if not col:
                raise ColumnNotFoundError(f'Cannot add index, column "{subj}" not defined in table "{self.name}".')
            i.subjects.append(col)

        i.table = self
        self.indexes.append(i)

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
        components = [f"Table({repr(self.name)}, {repr(self.columns)}"]
        if self.alias:
            components.append(f'alias={repr(self.alias)}')
        if self.indexes:
            components.append(f'indexes={repr(self.indexes)}')
        if self.note:
            components.append(f'note={repr(self.note)}')
        if self.header_color:
            components.append(f'header_color={repr(self.header_color)}')
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
        components = [f'EnumItem({repr(self.name)}']
        if self.note:
            components.append(f'note={repr(self.note)}')
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
        return f'Enum({repr(self.name)}, {repr(self.items)})'

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
        return f'EnumType({repr(self.name)}, {repr(self.items)})'

    def __str__(self):
        return self.name


class TableGroup:
    def __init__(self,
                 name: str,
                 items: List[str],
                 comment: Optional[str] = None):
        self.name = name
        self.items = items
        self.comment = comment

    def __repr__(self):
        return f'TableGroup({repr(self.name)}, {repr(self.items)})'

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
        components = [f'Project({repr(self.name)}']
        if self.items:
            components.append(f'items={repr(self.items)}')
        if self.note:
            components.append(f'note={repr(self.note)}')
        return ', '.join(components) + ')'
