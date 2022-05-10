from typing import Optional
from typing import Union
from typing import List
from typing import TYPE_CHECKING

from .base import SQLOjbect
from .note import Note
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import note_option_to_dbml
from pydbml.exceptions import TableNotFoundError

if TYPE_CHECKING:
    from .table import Table
    from .reference import Reference


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
                 note: Optional[Union['Note', str]] = None,
                 # ref_blueprints: Optional[List[ReferenceBlueprint]] = None,
                 comment: Optional[str] = None):
        self.schema = None
        self.name = name
        self.type = type_
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.autoinc = autoinc
        self.comment = comment
        self.note = Note(note)

        self.default = default
        self.table: Optional['Table'] = None

    def get_refs(self) -> List['Reference']:
        '''
        get all references related to this column (where this col is col1 in ref)
        '''
        if not self.table:
            raise TableNotFoundError('Table for the column is not set')
        return [ref for ref in self.table.get_refs() if ref.col1 == self]

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

        result = comment_to_sql(self.comment) if self.comment else ''
        result += ' '.join(components)
        return result

    @property
    def dbml(self):
        def default_to_str(val: str) -> str:
            if isinstance(val, str):
                if val.lower() in ('null', 'true', 'false'):
                    return val.lower()
                elif val.startswith('(') and val.endswith(')'):
                    return f'`{val[1:-1]}`'
                else:
                    return f"'{val}'"
            else:  # int or float or bool
                return val

        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'"{self.name}" {self.type}'

        options = [ref.dbml() for ref in self.get_refs() if ref.inline]
        if self.pk:
            options.append('pk')
        if self.autoinc:
            options.append('increment')
        if self.default:
            options.append(f'default: {default_to_str(self.default)}')
        if self.unique:
            options.append('unique')
        if self.not_null:
            options.append('not null')
        if self.note:
            options.append(note_option_to_dbml(self.note))

        if options:
            result += f' [{", ".join(options)}]'
        return result

    def __repr__(self):
        '''
        >>> Column('name', 'VARCHAR2')
        <Column 'name', 'VARCHAR2'>
        '''
        type_name = self.type if isinstance(self.type, str) else self.type.name
        return f'<Column {self.name!r}, {type_name!r}>'

    def __str__(self):
        '''
        >>> print(Column('name', 'VARCHAR2'))
        name[VARCHAR2]
        '''

        return f'{self.name}[{self.type}]'
