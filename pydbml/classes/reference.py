from typing import Collection
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from .base import SQLOjbect
from .column import Column
from pydbml import MANY_TO_ONE
from pydbml import ONE_TO_MANY
from pydbml import ONE_TO_ONE
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.exceptions import DBMLError


if TYPE_CHECKING:
    from .table import Table


class Reference(SQLOjbect):
    '''
    Class, representing a foreign key constraint.
    It is a separate object, which is not connected to Table or Column objects
    and its `sql` property contains the ALTER TABLE clause.
    '''
    required_attributes = ('type', 'table1', 'col1', 'table2', 'col2')

    def __init__(self,
                 type_: Literal[MANY_TO_ONE, ONE_TO_MANY, ONE_TO_ONE],
                 table1: 'Table',
                 col1: Union[Column, Collection[Column]],
                 table2: 'Table',
                 col2: Union[Column, Collection[Column]],
                 name: Optional[str] = None,
                 comment: Optional[str] = None,
                 on_update: Optional[str] = None,
                 on_delete: Optional[str] = None,
                 inline: bool = False):
        self.schema = None
        self.type = type_
        self.table1 = table1
        self.col1 = [col1] if isinstance(col1, Column) else list(col1)
        self.table2 = table2
        self.col2 = [col2] if isinstance(col2, Column) else list(col2)
        self.name = name if name else None
        self.comment = comment
        self.on_update = on_update
        self.on_delete = on_delete
        self.inline = inline

    def __repr__(self):
        '''
        >>> c1 = Column('c1', 'int')
        >>> c2 = Column('c2', 'int')
        >>> t1 = Table('t1')
        >>> t2 = Table('t2')
        >>> Reference('>', table1=t1, col1=c1, table2=t2, col2=c2)
        <Reference '>', 't1'.['c1'], 't2'.['c2']>
        >>> c12 = Column('c12', 'int')
        >>> c22 = Column('c22', 'int')
        >>> Reference('<', table1=t1, col1=[c1, c12], table2=t2, col2=(c2, c22))
        <Reference '<', 't1'.['c1', 'c12'], 't2'.['c2', 'c22']>
        '''

        components = [f"<Reference {self.type!r}"]
        components.append(f'{self.table1.name!r}.{[x.name for x in self.col1]!r}')
        components.append(f'{self.table2.name!r}.{[x.name for x in self.col2]!r}')
        return ', '.join(components) + '>'

    def __str__(self):
        '''
        >>> c1 = Column('c1', 'int')
        >>> c2 = Column('c2', 'int')
        >>> t1 = Table('t1')
        >>> t2 = Table('t2')
        >>> print(Reference('>', table1=t1, col1=c1, table2=t2, col2=c2))
        Reference(t1[c1] > t2[c2])
        >>> c12 = Column('c12', 'int')
        >>> c22 = Column('c22', 'int')
        >>> print(Reference('<', table1=t1, col1=[c1, c12], table2=t2, col2=(c2, c22)))
        Reference(t1[c1, c12] < t2[c2, c22])
        '''

        components = [f"Reference("]
        components.append(self.table1.name)
        components.append(f'[{", ".join(c.name for c in self.col1)}]')
        components.append(f' {self.type} ')
        components.append(self.table2.name)
        components.append(f'[{", ".join(c.name for c in self.col2)}]')
        return ''.join(components) + ')'

    @property
    def sql(self):
        '''
        Returns SQL of the reference:

        ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers ("id");

        '''
        self.check_attributes_for_sql()
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
                f'REFERENCES "{ref_table.name}" ("{ref_cols}")'
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
                f'ALTER TABLE "{t1.name}" ADD {c}FOREIGN KEY ({c1}) '
                f'REFERENCES "{t2.name}" ({c2})'
            )
            if self.on_update:
                result += f' ON UPDATE {self.on_update.upper()}'
            if self.on_delete:
                result += f' ON DELETE {self.on_delete.upper()}'
            return result + ';'

    @property
    def dbml(self):
        if self.inline:
            if len(self.col2) > 1:
                raise DBMLError('Cannot render DBML: composite ref cannot be inline')
            return f'ref: {self.type} {self.table2.name}.{self.col2[0].name}'
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
                f'"{self.table1.name}".{col1} '
                f'{self.type} '
                f'"{self.table2.name}".{col2}'
                f'{options_str}'
                '\n}'
            )
            return result
