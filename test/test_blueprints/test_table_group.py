from unittest import TestCase
from unittest.mock import Mock

from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.exceptions import ValidationError
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

    def test_build_with_schema(self) -> None:
        bp = TableGroupBlueprint(
            name='TestTableGroup',
            items=['myschema.table1', 'myschema.table2'],
            comment='Comment text'
        )
        with self.assertRaises(RuntimeError):
            bp.build()

        parserMock = Mock()
        parserMock.locate_table.side_effect = [
            Table(name='table1', schema='myschema'),
            Table(name='table2', schema='myschema')
        ]
        bp.parser = parserMock
        result = bp.build()
        self.assertIsInstance(result, TableGroup)
        locate_table_calls = parserMock.locate_table.call_args_list
        self.assertEqual(len(locate_table_calls), 2)
        self.assertEqual(locate_table_calls[0].args, ('myschema', 'table1'))
        self.assertEqual(locate_table_calls[1].args, ('myschema', 'table2'))
        for i in result.items:
            self.assertIsInstance(i, Table)

    def test_duplicate_table(self) -> None:
        bp = TableGroupBlueprint(
            name='TestTableGroup',
            items=['table1', 'table2', 'table1'],
            comment='Comment text'
        )

        parserMock = Mock()
        parserMock.locate_table.side_effect = [
            Table(name='table1'),
            Table(name='table2'),
            Table(name='table1')
        ]
        bp.parser = parserMock
        with self.assertRaises(ValidationError):
            bp.build()
