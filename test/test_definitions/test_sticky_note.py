from unittest import TestCase

from pyparsing import ParseSyntaxException

from pydbml.definitions.sticky_note import sticky_note


class TestSticky(TestCase):
    def test_single_quote(self) -> None:
        val = "note mynote {'test note'}"
        res = sticky_note.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, 'mynote')
        self.assertEqual(res[0].text, 'test note')

    def test_double_quote(self) -> None:
        val = 'note \n\nmynote\n\n {\n\n"test note"\n\n}'
        res = sticky_note.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, 'mynote')
        self.assertEqual(res[0].text, 'test note')

    def test_multiline(self) -> None:
        val = "note\nmynote\n{ '''line1\nline2\nline3'''}"
        res = sticky_note.parse_string(val, parseAll=True)
        self.assertEqual(res[0].name, 'mynote')
        self.assertEqual(res[0].text, 'line1\nline2\nline3')

    def test_unclosed_quote(self) -> None:
        val = 'note mynote{ "test note}'
        with self.assertRaises(ParseSyntaxException):
            sticky_note.parse_string(val, parseAll=True)

    def test_not_allowed_multiline(self) -> None:
        val = "note mynote { 'line1\nline2\nline3' }"
        with self.assertRaises(ParseSyntaxException):
            sticky_note.parse_string(val, parseAll=True)
