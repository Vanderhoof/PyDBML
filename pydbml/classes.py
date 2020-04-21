from __future__ import annotations


class Reference:
    ONE_TO_MANY = '<'
    MANY_TO_ONE = '>'
    ONE_TO_ONE = '-'

    REL_NAMES = {
        ONE_TO_MANY: 'One to many',
        MANY_TO_ONE: 'Many to one',
        ONE_TO_ONE: 'One to one'
    }

    def __init__(self,
                 type_=str,
                 name=None,
                 table1=None,
                 col1=None,
                 table2=None,
                 col2=None):
        self.type = type_
        self.name = name.strip('"') if name else None
        self.table1 = table1.strip('"') if table1 else None
        self.col1 = col1.strip('"') if col1 else None
        self.table2 = table2.strip('"') if table2 else None
        self.col2 = col2.strip('"') if col2 else None

    def __repr__(self):
        components = [f"Reference({repr(self.type)}"]
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
        return ', '.join(components) + ')'

    def __str__(self):
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''
        if self.type in (self.MANY_TO_ONE, self.ONE_TO_ONE):
            return (
                f'ALTER TABLE "{self.table1}" ADD {c}FOREIGN KEY ("{self.col1}") '
                f'REFERENCES "{self.table2} ("{self.col2}");'
            )
        else:
            return (
                f'ALTER TABLE "{self.table2}" ADD {c}FOREIGN KEY ("{self.col2}") '
                f'REFERENCES "{self.table1} ("{self.col1}");'
            )


class TableReference:
    def __init__(self,
                 col: str,
                 ref_table: str,
                 ref_col: str,
                 name=None):
        self.col = col
        self.ref_table = ref_table
        self.ref_col = ref_col
        self.name = name

    def __repr__(self):
        components = [f"TableReference({repr(self.col)}, {repr(self.ref_table)}, {repr(self.ref_col)}"]
        if self.name:
            components.append(f'name={repr(self.name)}')
        return ', '.join(components) + ')'

    def __str__(self):
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''
        return (
            f'{c}FOREIGN KEY ("{self.col}") '
            f'REFERENCES "{self.ref_table} ("{self.ref_col}")'
        )


class Note:
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        return f'Note({repr(self.text)})'


class Column:
    def __init__(self,
                 name: str,
                 type_: str,
                 unique: bool = False,
                 not_null: bool = False,
                 pk: bool = False,
                 autoinc: bool = False,
                 default=None,
                 note: str or None = None,
                 refs: list = None):
        self.name = name.strip('"')
        self.type = type_
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.autoinc = autoinc

        if isinstance(default, str):
            self.default = default.strip('`')
        else:
            self.default = default

        self.note = note or Note('')
        self.refs = refs or []
        for ref in self.refs:
            ref.col1 = self.name
        self._table = None

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, v: Table):
        self._table = v
        for ref in self.refs:
            ref.table1 = v.name

    def __str__(self):
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


class Index:
    def __init__(self,
                 subjects: list,
                 name: str or None = None,
                 table: str or None = None,  # TODO
                 unique: bool = False,
                 type_: str or None = None,
                 pk: bool = False,
                 note: Note or None = None):
        self.subjects = [s.strip('"') for s in subjects]
        self.name = name.strip('"') if name else None
        self.table = table
        self.unique = unique
        self.type = type_
        self.pk = pk
        self.note = note or Note('')

    def __repr__(self):
        components = [f"Index({self.subjects}"]
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
        keys = ', '.join(f'"{key}"' for key in self.subjects)
        if self.pk:
            return f'PRIMARY KEY ({keys})'

        components = ['CREATE']
        if self.unique:
            components.append('UNIQUE')
        components.append('INDEX')
        if self.name:
            components.append(f'"{self.name}"')
        components.append(f'ON "{self.table.name}"')
        components.append('(' + keys + ')')
        return ' '.join(components) + ';'


class Table:
    def __init__(self,
                 name: str,
                 alias: str or None = None,
                 note: Note or None = None,
                 header_color: str or None = None,
                 refs: list or None = None):
        self.name = name.strip('"')
        self.columns = []
        self.indexes = []
        self.column_dict = {}
        self.alias = alias.strip('"') if alias else None
        self.note = note or Note('')
        self.header_color = header_color
        self.refs = refs or []

    def add_column(self, c: Column):
        c.table = self
        self.columns.append(c)
        self.column_dict[c.name] = c

    def add_index(self, i: Index):
        i.table = self
        self.indexes.append(i)

    def __getitem__(self, k: int or str) -> Table:
        if isinstance(k, int):
            return self.columns[k]
        else:
            return self.column_dict[k]

    def __iter__(self):
        return iter(self.columns)

    def __repr__(self):
        components = [f"Table({self.name}, {self.columns}"]
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
        def indent(text):
            return '  ' + text
        components = [f'CREATE TABLE "{self.name}" (']
        body = []
        body.extend(indent(str(c)) for c in self.columns)
        body.extend(indent(str(i)) for i in self.indexes if i.pk)
        body.extend(indent(str(r)) for r in self.refs)
        components.append(',\n'.join(body))
        components.append(');\n')
        components.extend(str(i) + '\n' for i in self.indexes if not i.pk)
        return '\n'.join(components)


class EnumItem:
    def __init__(self,
                 name: str,
                 note: Note or None = None):
        self.name = name.strip('"')
        self.note = note or Note('')

    def __repr__(self):
        components = [f'EnumItem({repr(self.name)}']
        if self.note:
            components.append(f'note={repr(self.note)}')
        return ', '.join(components) + ')'

    def __str__(self):
        return self.name


class Enum:
    def __init__(self,
                 name: str,
                 items: list):
        self.name = name.strip('"')
        self.items = items

    def get_type(self):
        return EnumType(self.name, self.items)

    def __getitem__(self, key):
        return self.item[key]

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return f'Enum({repr(self.name)}, {repr(self.items)})'

    def __str__(self):
        items = []
        for item in self.items:
            items.append(f"  '{item}',")
        return f'CREATE TYPE "{self.name}" AS ENUM (\n' +\
               '\n'.join(items) +\
               '\n);'


class EnumType(Enum):
    def __repr__(self):
        return f'EnumType({repr(self.name)}, {repr(self.items)})'

    def __str__(self):
        return self.name


class TableGroup:
    def __init__(self,
                 name: str,
                 items: list):
        self.name = name.strip('"')
        self.items = items

    def __repr__(self):
        return f'TableGroup({repr(self.name)}, {repr(self.items)})'


class Project:
    def __init__(self,
                 name: str,
                 items: dict or None = None,
                 note: Note or None = None):
        self.name = name.strip('"')
        self.items = items
        self.note = note or Note('')

    def __repr__(self):
        components = [f'Project({repr(self.name)}']
        if self.items:
            components.append(f'items={repr(self.items)}')
        if self.note:
            components.append(f'note={repr(self.note)}')
        return ', '.join(components) + ')'
