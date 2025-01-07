from pydbml._classes.note import Note
from pydbml._classes.table_group import TableGroup
from pydbml.classes import Table
from pydbml.renderer.dbml.default import render_table_group


def test_render_table_group(table1: Table, table2: Table, table3: Table) -> None:
    tg = TableGroup(
        name="mygroup",
        items=[table1, table2, table3],
        comment="My comment",
        note=Note('Note line1\nNote line2')
    )
    expected = (
        '// My comment\n'
        'TableGroup mygroup {\n'
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
