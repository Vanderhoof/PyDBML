from itertools import chain
from typing import Collection
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from pydbml.constants import MANY_TO_MANY
from pydbml.constants import MANY_TO_ONE
from pydbml.constants import ONE_TO_MANY
from pydbml.constants import ONE_TO_ONE
from pydbml.exceptions import DBMLError
from pydbml.exceptions import TableNotFoundError
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from .base import SQLObject
from .column import Column
from .table import Table


class Reference(SQLObject):
    '''
    Class, representing a foreign key constraint.
    It is a separate object, which is not connected to Table or Column objects
    and its `sql` property contains the ALTER TABLE clause.
    '''
    required_attributes = ('type', 'col1', 'col2')

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
    def join_table(self) -> Optional['Table']:
        if self.type != MANY_TO_MANY:
            return None

        if self.table1 is None:
            raise TableNotFoundError(f"Cannot generate join table for {self}: table 1 is unknown")
        if self.table2 is None:
            raise TableNotFoundError(f"Cannot generate join table for {self}: table 2 is unknown")

        return Table(
            name=f'{self.table1.name}_{self.table2.name}',
            columns=(
                Column(name=f'{c.table.name}_{c.name}', type=c.type, not_null=True, pk=True)  # type: ignore
                for c in chain(self.col1, self.col2)
            ),
            abstract=True
        )

    @property
    def table1(self) -> Optional['Table']:
        self._validate()
        return self.col1[0].table if self.col1 else None

    @property
    def table2(self) -> Optional['Table']:
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

    def _validate_for_sql(self):
        for col in chain(self.col1, self.col2):
            if col.table is None:
                raise TableNotFoundError(f'Table on {col} is not set')

    def _generate_inline_sql(self, source_col: List['Column'], ref_col: List['Column']) -> str:
        result = comment_to_sql(self.comment) if self.comment else ''
        result += (
            f'{{c}}FOREIGN KEY ({self._col_names(source_col)}) '  # type: ignore
            f'REFERENCES {ref_col[0].table._get_full_name_for_sql()} ({self._col_names(ref_col)})'
        )
        if self.on_update:
            result += f' ON UPDATE {self.on_update.upper()}'
        if self.on_delete:
            result += f' ON DELETE {self.on_delete.upper()}'
        return result

    def _generate_not_inline_sql(self, c1: List['Column'], c2: List['Column']):
        result = comment_to_sql(self.comment) if self.comment else ''
        result += (
            f'ALTER TABLE {c1[0].table._get_full_name_for_sql()}'  # type: ignore
            f' ADD {{c}}FOREIGN KEY ({self._col_names(c1)})'
            f' REFERENCES {c2[0].table._get_full_name_for_sql()} ({self._col_names(c2)})'
        )
        if self.on_update:
            result += f' ON UPDATE {self.on_update.upper()}'
        if self.on_delete:
            result += f' ON DELETE {self.on_delete.upper()}'
        return result + ';'

    def _generate_many_to_many_sql(self) -> str:
        join_table = self.join_table
        table_sql = join_table.sql  # type: ignore

        n = len(self.col1)
        ref1_sql = self._generate_not_inline_sql(join_table.columns[:n], self.col1)  # type: ignore
        ref2_sql = self._generate_not_inline_sql(join_table.columns[n:], self.col2)  # type: ignore

        result = '\n\n'.join((table_sql, ref1_sql, ref2_sql))
        return result.format(c='')

    @staticmethod
    def _col_names(cols: List[Column]) -> str:
        return ', '.join(f'"{c.name}"' for c in cols)

    @property
    def sql(self) -> str:
        '''
        Returns SQL of the reference:

        ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers ("id");

        '''
        self.check_attributes_for_sql()
        self._validate_for_sql()

        if self.type == MANY_TO_MANY:
            return self._generate_many_to_many_sql()

        result = ''
        if self.inline:
            if self.type in (MANY_TO_ONE, ONE_TO_ONE):
                result = self._generate_inline_sql(self.col1, self.col2)
            elif self.type == ONE_TO_MANY:
                result = self._generate_inline_sql(self.col2, self.col1)
        else:
            if self.type in (MANY_TO_ONE, ONE_TO_ONE):
                result = self._generate_not_inline_sql(c1=self.col1, c2=self.col2)
            elif self.type == ONE_TO_MANY:
                result = self._generate_not_inline_sql(c1=self.col2, c2=self.col1)

        c = f'CONSTRAINT "{self.name}" ' if self.name else ''

        return result.format(c=c)

    @property
    def dbml(self) -> str:
        self._validate_for_sql()
        if self.inline:
            # settings are ignored for inline ref
            if len(self.col2) > 1:
                raise DBMLError('Cannot render DBML: composite ref cannot be inline')
            table_name = self.col2[0].table._get_full_name_for_sql()  # type: ignore
            return f'ref: {self.type} {table_name}."{self.col2[0].name}"'
        else:
            result = comment_to_dbml(self.comment) if self.comment else ''
            result += 'Ref'
            if self.name:
                result += f' {self.name}'

            if len(self.col1) == 1:
                col1 = f'"{self.col1[0].name}"'
            else:
                names = (f'"{c.name}"' for c in self.col1)
                col1 = f'({", ".join(names)})'

            if len(self.col2) == 1:
                col2 = f'"{self.col2[0].name}"'
            else:
                names = (f'"{c.name}"' for c in self.col2)
                col2 = f'({", ".join(names)})'

            options = []
            if self.on_update:
                options.append(f'update: {self.on_update}')
            if self.on_delete:
                options.append(f'delete: {self.on_delete}')

            options_str = f' [{", ".join(options)}]' if options else ''
            result += (
                ' {\n    '  # type: ignore
                f'{self.table1._get_full_name_for_sql()}.{col1} '
                f'{self.type} '
                f'{self.table2._get_full_name_for_sql()}.{col2}'
                f'{options_str}'
                '\n}'
            )
            return result
