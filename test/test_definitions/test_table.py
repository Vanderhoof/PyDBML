from unittest import TestCase

from pyparsing import ParseException
from pyparsing import ParseSyntaxException
from pyparsing import ParserElement

from pydbml.definitions.table import alias
from pydbml.definitions.table import header_color
from pydbml.definitions.table import table
from pydbml.definitions.table import table_body
from pydbml.definitions.table import table_settings


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestAlias(TestCase):
    def test_ok(self) -> None:
        val = 'as Alias'
        alias.parseString(val, parseAll=True)

    def test_nok(self) -> None:
        val = 'asalias'
        with self.assertRaises(ParseSyntaxException):
            alias.parseString(val, parseAll=True)


class TestHeaderColor(TestCase):
    def test_oneline(self) -> None:
        val = 'headercolor: #CCCCCC'
        res = header_color.parseString(val, parseAll=True)
        self.assertEqual(res['header_color'], '#CCCCCC')

    def test_multiline(self) -> None:
        val = 'headercolor:\n\n#E02'
        res = header_color.parseString(val, parseAll=True)
        self.assertEqual(res['header_color'], '#E02')


class TestTableSettings(TestCase):
    def test_one(self) -> None:
        val = '[headercolor: #E024DF]'
        res = table_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['header_color'], '#E024DF')

    def test_both(self) -> None:
        val = '[note: "note content", headercolor: #E024DF]'
        res = table_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['header_color'], '#E024DF')
        self.assertIn('note', res[0])


class TestTableBody(TestCase):
    def test_one_column(self) -> None:
        val = 'id integer [pk, increment]\n'
        res = table_body.parseString(val, parseAll=True)
        self.assertEqual(len(res['columns']), 1)

    def test_two_columns(self) -> None:
        val = 'id integer [pk, increment]\nname string\n'
        res = table_body.parseString(val, parseAll=True)
        self.assertEqual(len(res['columns']), 2)

    def test_columns_indexes(self) -> None:
        val = '''
id integer
country varchar [NOT NULL, ref: > countries.country_name]
booking_date date unique pk
indexes {
    (id, country) [pk] // composite primary key
}'''
        res = table_body.parseString(val, parseAll=True)
        self.assertEqual(len(res['columns']), 3)
        self.assertEqual(len(res['indexes']), 1)

    def test_columns_indexes_note(self) -> None:
        val = '''
id integer
country varchar [NOT NULL, ref: > countries.country_name]
booking_date date unique pk
note: 'mynote'
indexes {
    (id, country) [pk] // composite primary key
}'''
        res = table_body.parseString(val, parseAll=True)
        self.assertEqual(len(res['columns']), 3)
        self.assertEqual(len(res['indexes']), 1)
        self.assertIsNotNone(res['note'])
        val2 = '''
id integer
country varchar [NOT NULL, ref: > countries.country_name]
booking_date date unique pk
note {
    'mynote'
}
indexes {
    (id, country) [pk] // composite primary key
}'''
        res2 = table_body.parseString(val2, parseAll=True)
        self.assertEqual(len(res2['columns']), 3)
        self.assertEqual(len(res2['indexes']), 1)
        self.assertIsNotNone(res2['note'])

    def test_no_columns(self) -> None:
        val = '''
note: 'mynote'
indexes {
    (id, country) [pk] // composite primary key
}'''
        with self.assertRaises(ParseException):
            table_body.parseString(val, parseAll=True)

    def test_columns_after_indexes(self) -> None:
        val = '''
note: 'mynote'
indexes {
    (id, country) [pk] // composite primary key
}
id integer'''
        with self.assertRaises(ParseException):
            table_body.parseString(val, parseAll=True)


class TestTable(TestCase):
    def test_simple(self) -> None:
        val = 'table ids {\nid integer\n}'
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_alias(self) -> None:
        val = 'table ids as ii {\nid integer\n}'
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(res[0].alias, 'ii')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_settings(self) -> None:
        val = 'table ids as ii [headercolor: #ccc, note: "headernote"] {\nid integer\n}'
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(res[0].alias, 'ii')
        self.assertEqual(res[0].header_color, '#ccc')
        self.assertEqual(res[0].note.text, 'headernote')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_body_note(self) -> None:
        val = '''
table ids as ii [
  headercolor: #ccc,
  note: "headernote"]
{
  id integer
  note: "bodynote"
}'''
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(res[0].alias, 'ii')
        self.assertEqual(res[0].header_color, '#ccc')
        self.assertEqual(res[0].note.text, 'bodynote')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_indexes(self) -> None:
        val = '''
table ids as ii [
  headercolor: #ccc,
  note: "headernote"]
{
  id integer
  country varchar
  note: "bodynote"
  indexes {
      (id, country) [pk] // composite primary key
  }
}'''
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(res[0].alias, 'ii')
        self.assertEqual(res[0].header_color, '#ccc')
        self.assertEqual(res[0].note.text, 'bodynote')
        self.assertEqual(len(res[0].columns), 2)
        self.assertEqual(len(res[0].indexes), 1)
