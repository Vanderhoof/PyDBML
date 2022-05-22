from typing import Collection
from typing import Literal
from typing import Optional
from typing import Union
from typing import TYPE_CHECKING

from .base import SQLObject
from .column import Column
from pydbml.constants import MANY_TO_ONE
from pydbml.constants import ONE_TO_ONE
from pydbml.exceptions import DBMLError
from pydbml.exceptions import TableNotFoundError
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql

if TYPE_CHECKING:  # pragma: no cover
    from .table import Table


class Reference(SQLObject):
    '''
    Class, representing a foreign key constraint.
    It is a separate object, which is not connected to Table or Column objects
    and its `sql` property contains the ALTER TABLE clause.
    '''
    required_attributes = ('type', 'col1', 'col2')

    def __init__(self,
                 type: Literal['>', '<', '-'],
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
        self.inline = inline

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
        if self.table1 is None:
            raise TableNotFoundError('Table on col1 is not set')
        if self.table2 is None:
            raise TableNotFoundError('Table on col2 is not set')

    @property
    def sql(self):
        '''
        Returns SQL of the reference:

        ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers ("id");

        '''
        self.check_attributes_for_sql()
        self._validate_for_sql()
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''

        if self.inline:
            if self.type in (MANY_TO_ONE, ONE_TO_ONE):
                source_col = self.col1
                ref_table = self.table2
                ref_col = self.col2
            else:
                source_col = self.col2
                ref_table = self.table1
                ref_col = self.col1

            cols = '", "'.join(c.name for c in source_col)
            ref_cols = '", "'.join(c.name for c in ref_col)
            result = comment_to_sql(self.comment) if self.comment else ''
            result += (
                f'{c}FOREIGN KEY ("{cols}") '
                f'REFERENCES {ref_table._get_full_name_for_sql()} ("{ref_cols}")'
            )
            if self.on_update:
                result += f' ON UPDATE {self.on_update.upper()}'
            if self.on_delete:
                result += f' ON DELETE {self.on_delete.upper()}'
            return result
        else:
            if self.type in (MANY_TO_ONE, ONE_TO_ONE):
                t1 = self.table1
                c1 = ', '.join(f'"{c.name}"' for c in self.col1)
                t2 = self.table2
                c2 = ', '.join(f'"{c.name}"' for c in self.col2)
            else:
                t1 = self.table2
                c1 = ', '.join(f'"{c.name}"' for c in self.col2)
                t2 = self.table1
                c2 = ', '.join(f'"{c.name}"' for c in self.col1)

            result = comment_to_sql(self.comment) if self.comment else ''
            result += (
                f'ALTER TABLE {t1._get_full_name_for_sql()} ADD {c}FOREIGN KEY ({c1}) '
                f'REFERENCES {t2._get_full_name_for_sql()} ({c2})'
            )
            if self.on_update:
                result += f' ON UPDATE {self.on_update.upper()}'
            if self.on_delete:
                result += f' ON DELETE {self.on_delete.upper()}'
            return result + ';'

    @property
    def dbml(self):
        self._validate_for_sql()
        if self.inline:
            # settings are ignored for inline ref
            if len(self.col2) > 1:
                raise DBMLError('Cannot render DBML: composite ref cannot be inline')
            table_name = self.col2[0].table._get_full_name_for_sql()
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
                ' {\n    '
                f'{self.table1._get_full_name_for_sql()}.{col1} '
                f'{self.type} '
                f'{self.table2._get_full_name_for_sql()}.{col2}'
                f'{options_str}'
                '\n}'
            )
            return result
