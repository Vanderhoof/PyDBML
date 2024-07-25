from typing import List, Dict
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from pydbml.exceptions import TableNotFoundError
from .base import SQLObject, DBMLObject
from .enum import Enum
from .expression import Expression
from .note import Note

if TYPE_CHECKING:  # pragma: no cover
    from .table import Table
    from .reference import Reference


class Column(SQLObject, DBMLObject):
    '''Class representing table column.'''

    required_attributes = ('name', 'type')
    dont_compare_fields = ('table',)

    def __init__(self,
                 name: str,
                 type: Union[str, Enum],
                 unique: bool = False,
                 not_null: bool = False,
                 pk: bool = False,
                 autoinc: bool = False,
                 default: Optional[Union[str, int, bool, float, Expression]] = None,
                 note: Optional[Union[Note, str]] = None,
                 comment: Optional[str] = None,
                 properties: Union[Dict[str, str], None] = None
                 ):
        self.name = name
        self.type = type
        self.unique = unique
        self.not_null = not_null
        self.pk = pk
        self.autoinc = autoinc
        self.comment = comment
        self.note = Note(note)
        self.properties = properties if properties else {}

        self.default = default
        self.table: Optional['Table'] = None

    def __eq__(self, other: object) -> bool:
        if other is self:
            return True
        if not isinstance(other, self.__class__):
            return False
        self_table = self.table.full_name if self.table else None
        other_table = other.table.full_name if other.table else None
        if self_table != other_table:
            return False
        return super().__eq__(other)

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
