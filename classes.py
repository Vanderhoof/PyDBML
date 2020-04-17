from __future__ import annotations


class ColumnType:
    def __init__(self, name: str, args: str or None):
        self.name = name
        self.args = args

    def __repr__(self):
        components = [f'ColumnType({repr(self.name)}']
        if self.args:
            components.append(f'{repr(self.args)})')
        return ', '.join(components) + ')'

    def __str__(self):
        args = '(' + self.args + ')' if self.args else ''
        return self.name + args


# class ReferenceRegistry:
#     instance = None

#     def __new__(self, *args, **kwargs):
#         '''allowing only one instance of this class'''

#         if not self.instance:
#             self.instance = super(ReferenceRegistry, self).__new__(self, *args, **kwargs)
#             self.instance.registry = []
#             self.instance.awaiting = []
#         return self.instance

#     @classmethod
#     def clear(cls):
#         del cls.instance.registry
#         del cls.instance.awaiting
#         cls.instance = None


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
        self.name = name
        self.table1 = table1
        self.col1 = col1
        self.table2 = table2
        self.col2 = col2

    def __repr__(self):
        components = [f"Reference({repr(self.REL_NAMES[self.type])}"]
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
        return f'FOREIGN KEY ({self.col1}) REFERENCES {self.table2}({self.col2})'


class Note:
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return f'Note({repr(self.text)})'


class Column:
    def __init__(self,
                 name: str,
                 type_: ColumnType,
                 unique: bool = False,
                 not_null: bool = False,
                 pk: bool = False,
                 autoinc: bool = False,
                 default=None,
                 note: str or None = None,
                 ref: Reference or None = None):
        self.name = name
        self.type = type_
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.autoinc = autoinc
        self.default = default
        self.note = note
        self.ref = ref
        if self.ref:
            self.ref.col1 = self.name
        self._table = None

        @property
        def table(self):
            return self._table

        @table.setter
        def table(self, v: Table):
            self._table = v
            if self.ref:
                self.ref.table1 = v.name

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
                 unique: bool = False,
                 type_: str or None = None,
                 pk: bool = False,
                 note: Note or None = None):
        self.subjects = subjects
        self.name = name
        self.unique = unique
        self.type = type_
        self.pk = pk
        self.note = note

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


class Table:
    def __init__(self,
                 name: str,
                 alias: str or None = None,
                 indexes: list or None = None,
                 note: Note or None = None,
                 header_color: str or None = None):
        self.name = name
        self.columns = []
        self.alias = alias
        self.indexes = indexes
        self.note = note
        self.header_color = header_color

    def add_column(self, c: Column):
        c.table = self
        self.columns.append(c)

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
