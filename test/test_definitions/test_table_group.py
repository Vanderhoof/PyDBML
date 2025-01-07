from textwrap import dedent
from unittest import TestCase

from pyparsing import ParserElement

from pydbml.definitions.table_group import table_group


ParserElement.set_default_whitespace_chars(" \t\r")


class TestTableGroup(TestCase):
    def test_empty(self) -> None:
        val = "TableGroup name {}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")

    def test_fields(self) -> None:
        val = "TableGroup name {table1 table2}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])

    def test_comment(self) -> None:
        val = "//comment before\nTableGroup name\n{\ntable1\ntable2\n}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])
        self.assertEqual(res[0].comment, "comment before")

    def test_note_settings(self) -> None:
        val = "TableGroup name [note: 'My note'] \n{\ntable1\ntable2\n}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])
        self.assertEqual(res[0].note.text, "My note")

    def test_color(self) -> None:
        val = "TableGroup name [color: #FFF] \n{\ntable1\ntable2\n}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])
        self.assertEqual(res[0].color, "#FFF")

    def test_all_settings(self) -> None:
        val = "TableGroup name [color: #FFF, note: 'My note'] \n{\ntable1\ntable2\n}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])
        self.assertEqual(res[0].color, "#FFF")
        self.assertEqual(res[0].note.text, "My note")

    def test_note_body(self) -> None:
        val = dedent("""\
            TableGroup name {
                table1
                Note: '''
                    Note line1
                    Note line2
                '''
                table2
            }
        """)
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])
        self.assertIn("Note line1\n", res[0].note.text,)

    def test_note_settings_overriden_by_note_body(self) -> None:
        val = "TableGroup name [note: 'Settings note'] \n{\ntable1\nnote: 'Body note'\ntable2\n}"
        res = table_group.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, "name")
        self.assertEqual(res[0].items, ["table1", "table2"])
        self.assertEqual(res[0].note.text, "Body note")
