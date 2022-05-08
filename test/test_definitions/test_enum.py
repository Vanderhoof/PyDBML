from unittest import TestCase

from pyparsing import ParseSyntaxException
from pyparsing import ParserElement

from pydbml.definitions.enum import enum
from pydbml.definitions.enum import enum_item
from pydbml.definitions.enum import enum_settings


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestTableSettings(TestCase):
    def test_note(self) -> None:
        val = '[note: "note content"]'
        enum_settings.parseString(val, parseAll=True)

    def test_wrong(self) -> None:
        val = '[wrong]'
        with self.assertRaises(ParseSyntaxException):
            enum_settings.parseString(val, parseAll=True)


class TestEnumItem(TestCase):
    def test_no_settings(self) -> None:
        val = 'student'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')

    def test_settings(self) -> None:
        val = 'student [note: "our future, help us God"]'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')

    def test_comment_before(self) -> None:
        val = '//comment before\nstudent [note: "our future, help us God"]'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')
        self.assertEqual(res[0].comment, 'comment before')

    def test_comment_after(self) -> None:
        val = 'student [note: "our future, help us God"] //comment after'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')
        self.assertEqual(res[0].comment, 'comment after')

    def test_comment_both(self) -> None:
        val = '//comment before\nstudent [note: "our future, help us God"] //comment after'
        res = enum_item.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'student')
        self.assertEqual(res[0].note.text, 'our future, help us God')
        self.assertEqual(res[0].comment, 'comment after')


class TestEnum(TestCase):
    def test_singe_item(self) -> None:
        val = 'enum members {\nstudent\n}'
        res = enum.parseString(val, parseAll=True)
        self.assertEqual(len(res[0].items), 1)
        self.assertEqual(res[0].name, 'members')

    def test_several_items(self) -> None:
        val = 'enum members {janitor teacher\nstudent\nheadmaster\n}'
        res = enum.parseString(val, parseAll=True)
        self.assertEqual(len(res[0].items), 4)
        self.assertEqual(res[0].name, 'members')

    def test_comment(self) -> None:
        val = '//comment before\nenum members {janitor teacher\nstudent\nheadmaster\n}'
        res = enum.parseString(val, parseAll=True)
        self.assertEqual(len(res[0].items), 4)
        self.assertEqual(res[0].name, 'members')
        self.assertEqual(res[0].comment, 'comment before')

    def test_oneline(self) -> None:
        val = 'enum members {student}'
        with self.assertRaises(ParseSyntaxException):
            enum.parseString(val, parseAll=True)
