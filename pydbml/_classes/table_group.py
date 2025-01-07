from typing import List
from typing import Optional

from pydbml._classes.base import DBMLObject
from pydbml._classes.note import Note
from pydbml._classes.table import Table


class TableGroup(DBMLObject):
    '''
    TableGroup `items` parameter initially holds just the names of the tables,
    but after parsing the whole document, PyDBMLParseResults class replaces
    them with references to actual tables.
    '''
    dont_compare_fields = ('database',)

    def __init__(self,
                 name: str,
                 items: List[Table],
                 comment: Optional[str] = None,
                 note: Optional[Note] = None,
                 color: Optional[str] = None):
        self.database = None
        self.name = name
        self.items = items
        self.comment = comment
        self.note = note
        self.color = color

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
