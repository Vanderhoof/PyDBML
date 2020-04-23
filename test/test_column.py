from pyparsing import ParseException, ParseSyntaxException, ParserElement
from pydbml.definitions.column import (column_type, default, column_setting,
                                       column_settings, constraint, table_column)
from unittest import TestCase


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestColumnType(TestCase):
    def test_simple(self):
        val = 'int'
        res = column_type.parseString(val, parseAll=True)
        self.assertEqual(res[0], val)

    def test_quoted(self):
        val = '"mytype"'
        res = column_type.parseString(val, parseAll=True)
        self.assertEqual(res[0], val)

    def test_expression(self):
        val = 'varchar(255)'
        res = column_type.parseString(val, parseAll=True)
        self.assertEqual(res[0], val)

    def test_symbols(self):
        val = '(*#^)'
        with self.assertRaises(ParseException):
            column_type.parseString(val, parseAll=True)

    def test_string(self):
        val = "'mytype'"
        with self.assertRaises(ParseException):
            column_type.parseString(val, parseAll=True)


class TestDefault(TestCase):
    def test_string(self):
        val = "default: 'string'"
        val2 = "default: \n\n'string'"
        expected = 'string'
        res = default.parseString(val, parseAll=True)
        self.assertEqual(res[0], expected)
        res = default.parseString(val2, parseAll=True)
        self.assertEqual(res[0], expected)

    def test_expression(self):
        expr1 = 'datetime.now()'
        expr2 = 'datetime\nnow()'
        val = f"default: `{expr1}`"
        val2 = f"default: `{expr2}`"
        val3 = f"default: ``"
        res = default.parseString(val, parseAll=True)
        self.assertEqual(res[0], f'({expr1})')
        res = default.parseString(val2, parseAll=True)
        self.assertEqual(res[0], f'({expr2})')
        res = default.parseString(val3, parseAll=True)
        self.assertEqual(res[0], '()')

    def test_bool(self):
        vals = ['true', 'false', 'null']
        exps = [True, False, 'NULL']
        while len(vals) > 0:
            res = default.parseString(f'default: {vals.pop()}', parseAll=True)
            self.assertEqual(exps.pop(), res[0])

    def test_numbers(self):
        vals = [0, 17, 13.3, 2.0]
        while len(vals) > 0:
            cur = vals.pop()
            res = default.parseString(f'default: {cur}', parseAll=True)
            self.assertEqual((cur), res[0])

    def test_wrong(self):
        val = "default: now"
        with self.assertRaises(ParseException):
            default.parseString(val, parseAll=True)


class TestColumnSetting(TestCase):
    def test_pass(self):
        vals = ['not null',
                'null',
                'primary key',
                'pk',
                'unique',
                'default: 123',
                'ref: > table.column']
        for val in vals:
            column_setting.parseString(val, parseAll=True)

    def test_fail(self):
        vals = ['wrong',
                '`null`',
                '"pk"']
        for val in vals:
            with self.assertRaises(ParseException):
                column_setting.parseString(val, parseAll=True)


class TestColumnSettings(TestCase):
    def test_nulls(self):
        res = column_settings.parseString('[NULL]', parseAll=True)
        self.assertNotIn('not_null', res[0])
        res = column_settings.parseString('[NOT NULL]', parseAll=True)
        self.assertTrue(res[0]['not_null'])
        res = column_settings.parseString('[NULL, NOT NULL]', parseAll=True)
        self.assertTrue(res[0]['not_null'])
        res = column_settings.parseString('[NOT NULL, NULL]', parseAll=True)
        self.assertNotIn('not_null', res[0])

    def test_pk(self):
        res = column_settings.parseString('[pk]', parseAll=True)
        self.assertTrue(res[0]['pk'])
        res = column_settings.parseString('[primary key]', parseAll=True)
        self.assertTrue(res[0]['pk'])
        res = column_settings.parseString('[primary key, pk]', parseAll=True)
        self.assertTrue(res[0]['pk'])

    def test_unique_increment(self):
        res = column_settings.parseString('[unique, increment]', parseAll=True)
        self.assertTrue(res[0]['unique'])
        self.assertTrue(res[0]['autoinc'])

    def test_refs(self):
        res = column_settings.parseString('[ref: > table.column]', parseAll=True)
        self.assertEqual(len(res[0]['refs']), 1)
        res = column_settings.parseString('[ref: - table.column, ref: < table2.column2]', parseAll=True)
        self.assertEqual(len(res[0]['refs']), 2)

    def test_note_default(self):
        res = column_settings.parseString('[default: 123, note: "mynote"]', parseAll=True)
        self.assertIn('note', res[0])
        self.assertEqual(res[0]['default'], 123)

    def test_wrong(self):
        val = "[wrong]"
        with self.assertRaises(ParseSyntaxException):
            column_settings.parseString(val, parseAll=True)


class TestConstraint(TestCase):
    def test_should_parse(self):
        constraint.parseString('unique', parseAll=True)
        constraint.parseString('pk', parseAll=True)

    def test_should_fail(self):
        with self.assertRaises(ParseException):
            constraint.parseString('wrong', parseAll=True)


class TestColumn(TestCase):
    def test_no_settings(self):
        val = 'address varchar(255)\n'
        res = table_column.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'address')
        self.assertEqual(res[0].type, 'varchar(255)')

    def test_with_constraint(self):
        val = 'user_id integer unique\n'
        res = table_column.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'user_id')
        self.assertEqual(res[0].type, 'integer')
        self.assertTrue(res[0].unique)
        val2 = 'user_id integer pk unique\n'
        res2 = table_column.parseString(val2, parseAll=True)
        self.assertEqual(res2[0].name, 'user_id')
        self.assertEqual(res2[0].type, 'integer')
        self.assertTrue(res2[0].unique)
        self.assertTrue(res2[0].pk)

    def test_with_settings(self):
        val = "_test_ \"mytype\" [unique, not null, note: 'to include unit number']\n"
        res = table_column.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, '_test_')
        self.assertEqual(res[0].type, '\"mytype\"')
        self.assertTrue(res[0].unique)
        self.assertTrue(res[0].not_null)
        self.assertTrue(res[0].note is not None)

    def test_settings_and_constraints(self):
        val = "_test_ \"mytype\" unique pk [not null]\n"
        res = table_column.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, '_test_')
        self.assertEqual(res[0].type, '\"mytype\"')
        self.assertTrue(res[0].unique)
        self.assertTrue(res[0].not_null)
        self.assertTrue(res[0].pk)

    def test_comment_above(self):
        val = '//comment above\naddress varchar\n'
        res = table_column.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'address')
        self.assertEqual(res[0].type, 'varchar')
        self.assertEqual(res[0].comment, 'comment above')

    def test_comment_after(self):
        val = 'address varchar //comment after\n'
        res = table_column.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'address')
        self.assertEqual(res[0].type, 'varchar')
        self.assertEqual(res[0].comment, 'comment after')
        val2 = 'user_id integer pk unique //comment after\n'
        res2 = table_column.parseString(val2, parseAll=True)
        self.assertEqual(res2[0].name, 'user_id')
        self.assertEqual(res2[0].type, 'integer')
        self.assertTrue(res2[0].unique)
        self.assertTrue(res2[0].pk)
        self.assertEqual(res2[0].comment, 'comment after')
        val3 = "_test_ \"mytype\" unique pk [not null] //comment after\n"
        res3 = table_column.parseString(val3, parseAll=True)
        self.assertEqual(res3[0].name, '_test_')
        self.assertEqual(res3[0].type, '\"mytype\"')
        self.assertTrue(res3[0].unique)
        self.assertTrue(res3[0].not_null)
        self.assertTrue(res3[0].pk)
        self.assertEqual(res3[0].comment, 'comment after')
