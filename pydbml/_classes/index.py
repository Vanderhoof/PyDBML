from typing import List
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .base import SQLObject, DBMLObject
from .column import Column
from .expression import Expression
from .note import Note

if TYPE_CHECKING:  # pragma: no cover
    from .table import Table


class Index(SQLObject, DBMLObject):
    '''Class representing index.'''
    required_attributes = ('subjects', 'table')
    dont_compare_fields = ('table',)

    def __init__(self,
                 subjects: List[Union[str, Column, Expression]],
                 name: Optional[str] = None,
                 unique: bool = False,
                 type: Optional[Literal['hash', 'btree']] = None,
                 pk: bool = False,
                 note: Optional[Union[Note, str]] = None,
                 comment: Optional[str] = None):
        self.subjects = subjects
        self.table: Optional[Table] = None

        self.name = name if name else None
        self.unique = unique
        self.type = type
        self.pk = pk
        self.note = Note(note)
        self.comment = comment

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val: Note) -> None:
        self._note = val
        val.parent = self

    @property
    def subject_names(self):
        '''
        Returns updated list of subject names.
        '''
        return [s.name if isinstance(s, Column) else str(s) for s in self.subjects]

    def __repr__(self):
        '''
        <Index 'test', ['col', '(c*2)']>
        '''

        table_name = self.table.name if self.table else None
        return f"<Index {table_name!r}, {self.subject_names!r}>"

    def __str__(self):
        '''
        Index(test[col, (c*2)])
        '''

        table_name = self.table.name if self.table else ''
        subjects = ', '.join(self.subject_names)
        return f"Index({table_name}[{subjects}])"
