from unittest import TestCase
from unittest.mock import Mock

from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.parser.blueprints import TableGroupBlueprint


class TestTableGroupBlueprint(TestCase):
    def test_build(self) -> None:
        bp = TableGroupBlueprint(
            name='TestTableGroup',
            items=['table1', 'table2'],
            comment='Comment text'
        )
        with self.assertRaises(RuntimeError):
            bp.build()

        parserMock = Mock()
        parserMock.locate_table.side_effect = [
            Table(name='table1'),
            Table(name='table2')
        ]
        bp.parser = parserMock
        result = bp.build()
        self.assertIsInstance(result, TableGroup)
        self.assertEqual(parserMock.locate_table.call_count, 2)
        for i in result.items:
            self.assertIsInstance(i, Table)
