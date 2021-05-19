from unittest import TestCase

from pyparsing import ParserElement

from pydbml.definitions.table_group import table_group


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestProject(TestCase):
    def test_empty(self) -> None:
        val = 'TableGroup name {}'
        res = table_group.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')

    def test_fields(self) -> None:
        val = "TableGroup name {table1 table2}"
        res = table_group.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items, ['table1', 'table2'])

    def test_comment(self) -> None:
        val = "//comment before\nTableGroup name\n{\ntable1\ntable2\n}"
        res = table_group.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items, ['table1', 'table2'])
        self.assertEqual(res[0].comment, 'comment before')
