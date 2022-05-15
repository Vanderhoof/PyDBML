from typing import List
from typing import Optional
from typing import Union

from .table import Table
from pydbml.tools import comment_to_dbml


class TableGroup:
    '''
    TableGroup `items` parameter initially holds just the names of the tables,
    but after parsing the whole document, PyDBMLParseResults class replaces
    them with references to actual tables.
    '''

    def __init__(self,
                 name: str,
                 items: List[Table],
                 comment: Optional[str] = None):
        self.schema = None
        self.name = name
        self.items = items
        self.comment = comment

    def __repr__(self):
        """
        >>> tg = TableGroup('mygroup', ['t1', 't2'])
        >>> tg
        <TableGroup 'mygroup', ['t1', 't2']>
        >>> t1 = Table('t1')
        >>> t2 = Table('t2')
        >>> tg.items = [t1, t2]
        >>> tg
        <TableGroup 'mygroup', ['t1', 't2']>
        """

        items = [i if isinstance(i, str) else i.name for i in self.items]
        return f'<TableGroup {self.name!r}, {items!r}>'

    def __getitem__(self, key: int) -> Table:
        return self.items[key]

    def __iter__(self):
        return iter(self.items)

    @property
    def dbml(self):
        def item_to_str(val: Union[str, Table]) -> str:
            if isinstance(val, Table):
                return val.name
            else:
                return val

        result = comment_to_dbml(self.comment) if self.comment else ''
        result += f'TableGroup {self.name} {{\n'
        for i in self.items:
            result += f'    {item_to_str(i)}\n'
        result += '}'
        return result
