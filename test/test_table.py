from pyparsing import ParseException, ParseSyntaxException, ParserElement
from pydbml.definitions.table import (alias, header_color, table_settings,
                                      table_body, table)
from unittest import TestCase


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestAlias(TestCase):
    def test_ok(self):
        val = 'as Alias'
        alias.parseString(val, parseAll=True)

    def test_nok(self):
        val = 'asalias'
        with self.assertRaises(ParseSyntaxException):
            alias.parseString(val, parseAll=True)


class TestHeaderColor(TestCase):
    def test_oneline(self):
        val = 'headercolor: #CCCCCC'
        res = header_color.parseString(val, parseAll=True)
        self.assertEqual(res['header_color'], '#CCCCCC')

    def test_multiline(self):
        val = 'headercolor:\n\n#E02'
        res = header_color.parseString(val, parseAll=True)
        self.assertEqual(res['header_color'], '#E02')


class TestTableSettings(TestCase):
    def test_one(self):
        val = '[headercolor: #E024DF]'
        res = table_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['header_color'], '#E024DF')

    def test_both(self):
        val = '[note: "note content", headercolor: #E024DF]'
        res = table_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['header_color'], '#E024DF')
        self.assertIn('note', res[0])


class TestTableBody(TestCase):
    def test_one_column(self):
        val = 'id integer [pk, increment]\n'
        res = table_body.parseString(val, parseAll=True)
        self.assertEqual(len(res['columns']), 1)

    def test_two_columns(self):
        val = 'id integer [pk, increment]\nname string\n'
        res = table_body.parseString(val, parseAll=True)
        self.assertEqual(len(res['columns']), 2)

    def test_columns_indexes(self):
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

    def test_columns_indexes_note(self):
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

    def test_no_columns(self):
        val = '''
note: 'mynote'
indexes {
    (id, country) [pk] // composite primary key
}'''
        with self.assertRaises(ParseException):
            table_body.parseString(val, parseAll=True)

    def test_columns_after_indexes(self):
        val = '''
note: 'mynote'
indexes {
    (id, country) [pk] // composite primary key
}
id integer'''
        with self.assertRaises(ParseException):
            table_body.parseString(val, parseAll=True)


class TestTable(TestCase):
    def test_simple(self):
        val = 'table ids {\nid integer\n}'
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_alias(self):
        val = 'table ids as ii {\nid integer\n}'
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(res[0].alias, 'ii')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_settings(self):
        val = 'table ids as ii [headercolor: #ccc, note: "headernote"] {\nid integer\n}'
        res = table.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'ids')
        self.assertEqual(res[0].alias, 'ii')
        self.assertEqual(res[0].header_color, '#ccc')
        self.assertEqual(res[0].note.text, 'headernote')
        self.assertEqual(len(res[0].columns), 1)

    def test_with_body_note(self):
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

    def test_with_indexes(self):
        val = '''
table ids as ii [
  headercolor: #ccc,
  note: "headernote"]
{
  id integer
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
        self.assertEqual(len(res[0].columns), 1)
        self.assertEqual(len(res[0].indexes), 1)
