from unittest import TestCase

from pyparsing import ParseSyntaxException
from pyparsing import ParserElement

from pydbml.definitions.common import _c
from pydbml.definitions.common import comment
from pydbml.definitions.common import note
from pydbml.definitions.common import note_object


ParserElement.set_default_whitespace_chars(' \t\r')


class TestComment(TestCase):
    def test_comment_endstring(self) -> None:
        val = '//test comment'
        res = comment.parse_string(val, parseAll=True)
        self.assertEqual(res[0], 'test comment')

    def test_comment_endline(self) -> None:
        val = '//test comment\n\n\n\n\n'
        res = comment.parse_string(val)
        self.assertEqual(res[0], 'test comment')

    def test_multiline_comment(self) -> None:
        val = '/*test comment*/'
        res = comment.parse_string(val)
        self.assertEqual(res[0], 'test comment')

        val2 = '/*\nline1\nline2\nline3\n*/'
        res2 = comment.parse_string(val2)
        self.assertEqual(res2[0], '\nline1\nline2\nline3\n')


class Test_c(TestCase):
    def test_comment(self) -> None:
        val = '\n\n\n\n//comment line 1\n\n//comment line 2'
        res = _c.parse_string(val, parseAll=True)
        self.assertEqual(list(res), ['comment line 1', 'comment line 2'])


class TestNote(TestCase):
    def test_single_quote(self) -> None:
        val = "note: 'test note'"
        res = note.parse_string(val, parseAll=True)
        self.assertEqual(res[0].text, 'test note')

    def test_double_quote(self) -> None:
        val = 'note: \n "test note"'
        res = note.parse_string(val, parseAll=True)
        self.assertEqual(res[0].text, 'test note')

    def test_multiline(self) -> None:
        val = "note: '''line1\nline2\nline3'''"
        res = note.parse_string(val, parseAll=True)
        self.assertEqual(res[0].text, 'line1\nline2\nline3')

    def test_unclosed_quote(self) -> None:
        val = 'note: "test note'
        with self.assertRaises(ParseSyntaxException):
            note.parse_string(val, parseAll=True)

    def test_not_allowed_multiline(self) -> None:
        val = "note: 'line1\nline2\nline3'"
        with self.assertRaises(ParseSyntaxException):
            note.parse_string(val, parseAll=True)


class TestNoteObject(TestCase):
    def test_single_quote(self) -> None:
        val = "note {'test note'}"
        res = note_object.parse_string(val, parseAll=True)
        self.assertEqual(res[0].text, 'test note')

    def test_double_quote(self) -> None:
        val = 'note \n\n {\n\n"test note"\n\n}'
        res = note_object.parse_string(val, parseAll=True)
        self.assertEqual(res[0].text, 'test note')

    def test_multiline(self) -> None:
        val = "note\n{ '''line1\nline2\nline3'''}"
        res = note_object.parse_string(val, parseAll=True)
        self.assertEqual(res[0].text, 'line1\nline2\nline3')

    def test_unclosed_quote(self) -> None:
        val = 'note{ "test note}'
        with self.assertRaises(ParseSyntaxException):
            note_object.parse_string(val, parseAll=True)

    def test_not_allowed_multiline(self) -> None:
        val = "note { 'line1\nline2\nline3' }"
        with self.assertRaises(ParseSyntaxException):
            note_object.parse_string(val, parseAll=True)
