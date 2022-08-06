from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .base import SQLObject
from .expression import Expression
from .enum import Enum
from .note import Note
from pydbml.exceptions import TableNotFoundError
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import note_option_to_dbml

if TYPE_CHECKING:  # pragma: no cover
    from .table import Table
    from .reference import Reference


class Column(SQLObject):
    '''Class representing table column.'''

    required_attributes = ('name', 'type')

    def __init__(self,
                 name: str,
                 type: Union[str, Enum],
                 unique: bool = False,
                 not_null: bool = False,
                 pk: bool = False,
                 autoinc: bool = False,
                 default: Optional[Union[str, int, bool, float, Expression]] = None,
                 note: Optional[Union['Note', str]] = None,
                 # ref_blueprints: Optional[List[ReferenceBlueprint]] = None,
                 comment: Optional[str] = None):
        self.name = name
        self.type = type
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.autoinc = autoinc
        self.comment = comment
        self.note = Note(note)

        self.default = default
        self.table: Optional['Table'] = None

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val: Note) -> None:
        self._note = val
        val.parent = self

    def get_refs(self) -> List['Reference']:
        '''
        get all references related to this column (where this col is col1 in)
        '''
        if not self.table:
            raise TableNotFoundError('Table for the column is not set')
        return [ref for ref in self.table.get_refs() if self in ref.col1]

    @property
    def database(self):
        return self.table.database if self.table else None

    @property
    def sql(self):
        '''
        Returns inline SQL of the column, which should be a part of table definition:

        "id" integer PRIMARY KEY AUTOINCREMENT
        '''

        self.check_attributes_for_sql()
        components = [f'"{self.name}"']
        if isinstance(self.type, Enum):
            components.append(self.type._get_full_name_for_sql())
        else:
            components.append(str(self.type))

        table_has_composite_pk = False if self.table is None else self.table._has_composite_pk()
        if self.pk and not table_has_composite_pk:  # comp-PKs are rendered in table sql
            components.append('PRIMARY KEY')
        if self.autoinc:
            components.append('AUTOINCREMENT')
        if self.unique:
            components.append('UNIQUE')
        if self.not_null:
            components.append('NOT NULL')
        if self.default is not None:
            default = self.default.sql \
                if isinstance(self.default, Expression) else self.default
            components.append(f'DEFAULT {default}')

        result = comment_to_sql(self.comment) if self.comment else ''
        result += ' '.join(components)
        return result

    @property
    def dbml(self):
        def default_to_str(val: Union[Expression, str]) -> str:
            if isinstance(val, str):
                if val.lower() in ('null', 'true', 'false'):
                    return val.lower()
                else:
                    return f"'{val}'"
            elif isinstance(val, Expression):
                return val.dbml
            else:  # int or float or bool
                return val

        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'"{self.name}" '
        if isinstance(self.type, Enum):
            result += self.type._get_full_name_for_sql()
        else:
            result += self.type

        options = [ref.dbml for ref in self.get_refs() if ref.inline]
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
