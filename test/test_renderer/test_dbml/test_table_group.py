from pydbml._classes.note import Note
from pydbml._classes.table_group import TableGroup
from pydbml.classes import Table
from pydbml.renderer.dbml.default import render_table_group


class TestTableGroup:
    @staticmethod
    def test_simple(table1: Table, table2: Table, table3: Table) -> None:
        tg = TableGroup(
            name="mygroup",
            items=[table1, table2, table3],
        )
        expected = (
            'TableGroup mygroup {\n'
            '    "products"\n'
            '    "products"\n'
            '    "orders"\n'
            '}'
        )
        assert render_table_group(tg) == expected

    @staticmethod
    def test_full(table1: Table, table2: Table, table3: Table) -> None:
        tg = TableGroup(
            name="mygroup",
            items=[table1, table2, table3],
            comment="My comment",
            note=Note('Note line1\nNote line2'),
            color='#FFF'
        )
        expected = (
            '// My comment\n'
            'TableGroup mygroup [color: #FFF] {\n'
            '    "products"\n'
            '    "products"\n'
            '    "orders"\n'
            '    Note {\n'
            "        '''\n"
            '        Note line1\n'
            "        Note line2'''\n"
            '    }\n'
            '}'
        )
        assert render_table_group(tg) == expected
