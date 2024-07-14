from itertools import chain
from typing import Collection
from typing import Literal
from typing import Optional
from typing import Union

from pydbml.constants import MANY_TO_MANY
from pydbml.exceptions import DBMLError
from pydbml.exceptions import TableNotFoundError
from .base import SQLObject, DBMLObject
from .column import Column
from .table import Table


class Reference(SQLObject, DBMLObject):
    '''
    Class, representing a foreign key constraint.
    It is a separate object, which is not connected to Table or Column objects
    and its `sql` property contains the ALTER TABLE clause.
    '''
    required_attributes = ('type', 'col1', 'col2')
    dont_compare_fields = ('database', '_inline')

    def __init__(self,
                 type: Literal['>', '<', '-', '<>'],
                 col1: Union[Column, Collection[Column]],
                 col2: Union[Column, Collection[Column]],
                 name: Optional[str] = None,
                 comment: Optional[str] = None,
                 on_update: Optional[str] = None,
                 on_delete: Optional[str] = None,
                 inline: bool = False):
        self.database = None
        self.type = type
        self.col1 = [col1] if isinstance(col1, Column) else list(col1)
        self.col2 = [col2] if isinstance(col2, Column) else list(col2)
        self.name = name if name else None
        self.comment = comment
        self.on_update = on_update
        self.on_delete = on_delete
        self._inline = inline

    @property
    def inline(self) -> bool:
        return self._inline and not self.type == MANY_TO_MANY

    @inline.setter
    def inline(self, val) -> None:
        self._inline = val

    @property
    def join_table(self) -> Optional[Table]:
        if self.type != MANY_TO_MANY:
            return None

        if self.table1 is None:
            raise TableNotFoundError(f"Cannot generate join table for {self}: table 1 is unknown")
        if self.table2 is None:
            raise TableNotFoundError(f"Cannot generate join table for {self}: table 2 is unknown")

        return Table(
            name=f'{self.table1.name}_{self.table2.name}',
            schema=self.table1.schema,
            columns=(
                Column(name=f'{c.table.name}_{c.name}', type=c.type, not_null=True, pk=True)  # type: ignore
                for c in chain(self.col1, self.col2)
            ),
            abstract=True
        )

    @property
    def table1(self) -> Optional[Table]:
        self._validate()
        return self.col1[0].table if self.col1 else None

    @property
    def table2(self) -> Optional[Table]:
        self._validate()
        return self.col2[0].table if self.col2 else None

    def __repr__(self):
        '''
        >>> c1 = Column('c1', 'int')
        >>> c2 = Column('c2', 'int')
        >>> Reference('>', col1=c1, col2=c2)
        <Reference '>', ['c1'], ['c2']>
        >>> c12 = Column('c12', 'int')
        >>> c22 = Column('c22', 'int')
        >>> Reference('<', col1=[c1, c12], col2=(c2, c22))
        <Reference '<', ['c1', 'c12'], ['c2', 'c22']>
        '''

        col1 = ', '.join(f'{c.name!r}' for c in self.col1)
        col2 = ', '.join(f'{c.name!r}' for c in self.col2)
        return f"<Reference {self.type!r}, [{col1}], [{col2}]>"

    def __str__(self):
        '''
        >>> c1 = Column('c1', 'int')
        >>> c2 = Column('c2', 'int')
        >>> print(Reference('>', col1=c1, col2=c2))
        Reference([c1] > [c2]
        >>> c12 = Column('c12', 'int')
        >>> c22 = Column('c22', 'int')
        >>> print(Reference('<', col1=[c1, c12], col2=(c2, c22)))
        Reference([c1, c12] < [c2, c22]
        '''

        col1 = ', '.join(f'{c.name}' for c in self.col1)
        col2 = ', '.join(f'{c.name}' for c in self.col2)
        return f"Reference([{col1}] {self.type} [{col2}]"

    def _validate(self):
        table1 = self.col1[0].table
        if any(c.table != table1 for c in self.col1):
            raise DBMLError('Columns in col1 are from different tables')

        table2 = self.col2[0].table
        if any(c.table != table2 for c in self.col2):
            raise DBMLError('Columns in col2 are from different tables')
