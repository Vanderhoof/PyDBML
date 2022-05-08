from __future__ import annotations

from typing import Any
from typing import Collection
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from pydbml.parser.blueprints import IndexBlueprint
from pydbml.parser.blueprints import ReferenceBlueprint
from pydbml.exceptions import AttributeMissingError
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import IndexNotFoundError
from pydbml.exceptions import UnknownSchemaError
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import indent
from pydbml.tools import note_option_to_dbml


class SQLOjbect:
    '''
    Base class for all SQL objects.
    '''
    required_attributes: Tuple[str, ...] = ()

    def check_attributes_for_sql(self):
        '''
        Check if all attributes, required for rendering SQL are set in the
        instance. If some attribute is missing, raise AttributeMissingError
        '''
        for attr in self.required_attributes:
            if getattr(self, attr) is None:
                raise AttributeMissingError(
                    f'Cannot render SQL. Missing required attribute "{attr}".'
                )

    def __setattr__(self, name: str, value: Any):
        """
        Required for type testing with MyPy.
        """
        super().__setattr__(name, value)

    def __eq__(self, other: object) -> bool:
        """
        Two instances of the same SQLObject subclass are equal if all their
        attributes are equal.
        """

        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False


class TableReference(SQLOjbect):
    '''
    Class, representing a foreign key constraint.
    This object should be assigned to the `refs` attribute of a Table object.
    Its `sql` property contains the inline definition of the FOREIGN KEY clause.
    '''
    required_attributes = ('col', 'ref_table', 'ref_col')

    def __init__(self,
                 col: Union[Column, List[Column]],
                 ref_table: Table,
                 ref_col: Union[Column, List[Column]],
                 name: Optional[str] = None,
                 on_delete: Optional[str] = None,
                 on_update: Optional[str] = None):
        self.col = [col] if isinstance(col, Column) else list(col)
        self.ref_table = ref_table
        self.ref_col = [ref_col] if isinstance(ref_col, Column) else list(ref_col)
        self.name = name
        self.on_update = on_update
        self.on_delete = on_delete

    def __repr__(self):
        '''
        >>> c1 = Column('c1', 'int')
        >>> c2 = Column('c2', 'int')
        >>> t2 = Table('t2')
        >>> TableReference(col=c1, ref_table=t2, ref_col=c2)
        <TableReference ['c1'], 't2'.['c2']>
        >>> c12 = Column('c12', 'int')
        >>> c22 = Column('c22', 'int')
        >>> TableReference(col=[c1, c12], ref_table=t2, ref_col=(c2, c22))
        <TableReference ['c1', 'c12'], 't2'.['c2', 'c22']>
        '''

        col_names = [c.name for c in self.col]
        ref_col_names = [c.name for c in self.ref_col]
        return f"<TableReference {col_names!r}, {self.ref_table.name!r}.{ref_col_names!r}>"

    def __str__(self):
        '''
        >>> c1 = Column('c1', 'int')
        >>> c2 = Column('c2', 'int')
        >>> t2 = Table('t2')
        >>> print(TableReference(col=c1, ref_table=t2, ref_col=c2))
        TableReference([c1] > t2[c2])
        >>> c12 = Column('c12', 'int')
        >>> c22 = Column('c22', 'int')
        >>> print(TableReference(col=[c1, c12], ref_table=t2, ref_col=(c2, c22)))
        TableReference([c1, c12] > t2[c2, c22])
        '''

        components = [f"TableReference("]
        components.append(f'[{", ".join(c.name for c in self.col)}]')
        components.append(' > ')
        components.append(self.ref_table.name)
        components.append(f'[{", ".join(c.name for c in self.ref_col)}]')
        return ''.join(components) + ')'

    @property
    def sql(self):
        '''
        Returns inline SQL of the reference, which should be a part of table definition:

        FOREIGN KEY ("order_id") REFERENCES "orders ("id")

        '''
        self.check_attributes_for_sql()
        c = f'CONSTRAINT "{self.name}" ' if self.name else ''
        cols = '", "'.join(c.name for c in self.col)
        ref_cols = '", "'.join(c.name for c in self.ref_col)
        result = (
            f'{c}FOREIGN KEY ("{cols}") '
            f'REFERENCES "{self.ref_table.name}" ("{ref_cols}")'
        )
        if self.on_update:
            result += f' ON UPDATE {self.on_update.upper()}'
        if self.on_delete:
            result += f' ON DELETE {self.on_delete.upper()}'
        return result








class EnumType(Enum):
    '''
    Enum object, intended to be put in the `type` attribute of a column.

    >>> en = EnumItem('en-US')
    >>> ru = EnumItem('ru-RU')
    >>> EnumType('languages', [en, ru])
    <EnumType 'languages', ['en-US', 'ru-RU']>
    >>> print(_)
    languages
    '''

    pass




