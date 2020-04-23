from pyparsing import ParseException, ParseSyntaxException, ParserElement
from pydbml.definitions.reference import (relation, ref_inline, on_option,
                                          ref_settings, ref_short, ref_long)
from unittest import TestCase


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestRelation(TestCase):
    def test_ok(self):
        vals = ['>', '-', '<']
        for v in vals:
            relation.parseString(v, parseAll=True)

    def test_nok(self):
        val = 'wrong'
        with self.assertRaises(ParseException):
            relation.parseString(val, parseAll=True)


class TestInlineRelation(TestCase):
    def test_ok(self):
        val = 'ref: < table.column'
        res = ref_inline.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '<')
        self.assertEqual(res[0].table2, 'table')
        self.assertEqual(res[0].col2, 'column')
        self.assertIsNone(res[0].table1)
        self.assertIsNone(res[0].col1)

    def test_nok(self):
        vals = [
            'ref:\n< table.column',
            'ref: table.column',
            'ref: < tablecolumn',
            'ref:<'
        ]
        for v in vals:
            with self.assertRaises(ParseSyntaxException):
                ref_inline.parseString(v)


class TestOnOption(TestCase):
    def test_ok(self):
        vals = [
            'no action',
            'restrict',
            'cascade',
            'set null',
            'set default'
        ]
        for v in vals:
            on_option.parseString(v, parseAll=True)

    def test_nok(self):
        val = 'wrong'
        with self.assertRaises(ParseException):
            on_option.parseString(val, parseAll=True)


class TestRefSettings(TestCase):
    def test_one_setting(self):
        val = '[delete: cascade]'
        res = ref_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['on_delete'], 'cascade')

    def test_two_settings_multiline(self):
        val = '[\ndelete:\ncascade\n,\nupdate:\nrestrict\n]'
        res = ref_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['on_delete'], 'cascade')
        self.assertEqual(res[0]['on_update'], 'restrict')


class TestRefShort(TestCase):
    def test_no_name(self):
        val = 'ref: table1.col1 > table2.col2'
        res = ref_short.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')

    def test_name(self):
        val = 'ref name: table1.col1 > table2.col2'
        res = ref_short.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')

    def test_with_settings(self):
        val = 'ref name: table1.col1 > table2.col2 [update: cascade, delete: restrict]'
        res = ref_short.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].on_update, 'cascade')
        self.assertEqual(res[0].on_delete, 'restrict')

    def test_newline(self):
        val = 'ref\nname: table1.col1 > table2.col2'
        with self.assertRaises(ParseException):
            ref_short.parseString(val, parseAll=True)
        val2 = 'ref name: table1.col1\n> table2.col2'
        with self.assertRaises(ParseSyntaxException):
            ref_short.parseString(val2, parseAll=True)

    def test_comment_above(self):
        val = '//comment above\nref name: table1.col1 > table2.col2'
        res = ref_short.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].comment, 'comment above')

    def test_comment_after(self):
        val = 'ref name: table1.col1 > table2.col2 //comment after'
        res = ref_short.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].comment, 'comment after')
        val2 = 'ref name: table1.col1 > table2.col2 [update: cascade, delete: restrict] //comment after'
        res2 = ref_short.parseString(val2, parseAll=True)
        self.assertEqual(res2[0].type, '>')
        self.assertEqual(res2[0].table1, 'table1')
        self.assertEqual(res2[0].col1, 'col1')
        self.assertEqual(res2[0].table2, 'table2')
        self.assertEqual(res2[0].col2, 'col2')
        self.assertEqual(res2[0].name, 'name')
        self.assertEqual(res2[0].on_update, 'cascade')
        self.assertEqual(res2[0].on_delete, 'restrict')
        self.assertEqual(res2[0].comment, 'comment after')

    def test_comment_both(self):
        val = '//comment above\nref name: table1.col1 > table2.col2 //comment after'
        res = ref_short.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].comment, 'comment after')
        val2 = '//comment above\nref name: table1.col1 > table2.col2 [update: cascade, delete: restrict] //comment after'
        res2 = ref_short.parseString(val2, parseAll=True)
        self.assertEqual(res2[0].type, '>')
        self.assertEqual(res2[0].table1, 'table1')
        self.assertEqual(res2[0].col1, 'col1')
        self.assertEqual(res2[0].table2, 'table2')
        self.assertEqual(res2[0].col2, 'col2')
        self.assertEqual(res2[0].name, 'name')
        self.assertEqual(res2[0].on_update, 'cascade')
        self.assertEqual(res2[0].on_delete, 'restrict')
        self.assertEqual(res2[0].comment, 'comment after')


class TestRefLong(TestCase):
    def test_no_name(self):
        val = 'ref  {table1.col1 > table2.col2}'
        res = ref_long.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')

    def test_name(self):
        val = 'ref\nname\n{\ntable1.col1 > table2.col2\n}'
        res = ref_long.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')

    def test_with_settings(self):
        val = 'ref name {\ntable1.col1 > table2.col2 [update: cascade, delete: restrict]\n}'
        res = ref_long.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].on_update, 'cascade')
        self.assertEqual(res[0].on_delete, 'restrict')

    def test_comment_above(self):
        val = '//comment above\nref name {\ntable1.col1 > table2.col2\n}'
        res = ref_long.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].comment, 'comment above')

    def test_comment_after(self):
        val = 'ref name {\ntable1.col1 > table2.col2 //comment after\n}'
        res = ref_long.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].comment, 'comment after')
        val2 = 'ref name {\ntable1.col1 > table2.col2 [update: cascade, delete: restrict] //comment after\n}'
        res2 = ref_long.parseString(val2, parseAll=True)
        self.assertEqual(res2[0].type, '>')
        self.assertEqual(res2[0].table1, 'table1')
        self.assertEqual(res2[0].col1, 'col1')
        self.assertEqual(res2[0].table2, 'table2')
        self.assertEqual(res2[0].col2, 'col2')
        self.assertEqual(res2[0].name, 'name')
        self.assertEqual(res2[0].on_update, 'cascade')
        self.assertEqual(res2[0].on_delete, 'restrict')
        self.assertEqual(res2[0].comment, 'comment after')

    def test_comment_both(self):
        val = '//comment above\nref name {\ntable1.col1 > table2.col2 //comment after\n}'
        res = ref_long.parseString(val, parseAll=True)
        self.assertEqual(res[0].type, '>')
        self.assertEqual(res[0].table1, 'table1')
        self.assertEqual(res[0].col1, 'col1')
        self.assertEqual(res[0].table2, 'table2')
        self.assertEqual(res[0].col2, 'col2')
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].comment, 'comment after')
        val2 = '//comment above\nref name {\ntable1.col1 > table2.col2 [update: cascade, delete: restrict] //comment after\n}'
        res2 = ref_long.parseString(val2, parseAll=True)
        self.assertEqual(res2[0].type, '>')
        self.assertEqual(res2[0].table1, 'table1')
        self.assertEqual(res2[0].col1, 'col1')
        self.assertEqual(res2[0].table2, 'table2')
        self.assertEqual(res2[0].col2, 'col2')
        self.assertEqual(res2[0].name, 'name')
        self.assertEqual(res2[0].on_update, 'cascade')
        self.assertEqual(res2[0].on_delete, 'restrict')
        self.assertEqual(res2[0].comment, 'comment after')
