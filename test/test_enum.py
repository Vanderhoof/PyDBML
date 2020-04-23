from pyparsing import ParseException, ParseSyntaxException, ParserElement
from pydbml.definitions.enum import (enum_settings, enum_item, enum)
from unittest import TestCase


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestTableSettings(TestCase):
    def test_note(self):
        val = '[note: "note content"]'
        enum_settings.parseString(val, parseAll=True)

    def test_wrong(self):
        val = '[wrong]'
        with self.assertRaises(ParseSyntaxException):
            enum_settings.parseString(val, parseAll=True)


class TestEnumItem(TestCase):
    def test_no_settings(self):
        val = 'student'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')

    def test_settings(self):
        val = 'student [note: "our future, help us God"]'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')

    def test_comment_before(self):
        val = '//comment before\nstudent [note: "our future, help us God"]'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')
        self.assertEqual(res[0].comment, 'comment before')

    def test_comment_after(self):
        val = 'student [note: "our future, help us God"] //comment after'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')
        self.assertEqual(res[0].comment, 'comment after')

    def test_comment_both(self):
        val = '//comment before\nstudent [note: "our future, help us God"] //comment after'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')
        self.assertEqual(res[0].comment, 'comment after')


class TestEnum(TestCase):
    def test_singe_item(self):
        val = 'enum members {\nstudent\n}'
        res = enum.parseString(val, parseAll=True)
        self.assertEqual(len(res[0].items), 1)
        self.assertEqual(res[0].name, 'members')

    def test_several_items(self):
        val = 'enum members {janitor teacher\nstudent\nheadmaster\n}'
        res = enum.parseString(val, parseAll=True)
        self.assertEqual(len(res[0].items), 4)
        self.assertEqual(res[0].name, 'members')

    def test_comment(self):
        val = '//comment before\nenum members {janitor teacher\nstudent\nheadmaster\n}'
        res = enum.parseString(val, parseAll=True)
        self.assertEqual(len(res[0].items), 4)
        self.assertEqual(res[0].name, 'members')
        self.assertEqual(res[0].comment, 'comment before')

    def test_oneline(self):
        val = 'enum members {student}'
        with self.assertRaises(ParseSyntaxException):
            enum.parseString(val, parseAll=True)
