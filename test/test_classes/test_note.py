from pydbml.classes import Note
from unittest import TestCase


class TestNote(TestCase):
    def test_init_types(self):
        n1 = Note('My note text')
        n2 = Note(3)
        n3 = Note([1, 2, 3])
        n4 = Note(None)
        n5 = Note(n1)

        self.assertEqual(n1.text, 'My note text')
        self.assertEqual(n2.text, '3')
        self.assertEqual(n3.text, '[1, 2, 3]')
        self.assertEqual(n4.text, '')
        self.assertEqual(n5.text, 'My note text')

    def test_oneline(self):
        note = Note('One line of note text')
        expected = \
'''Note {
    'One line of note text'
}'''
        self.assertEqual(note.dbml, expected)

    def test_forced_multiline(self):
        note = Note('The number of spaces you use to indent a block string\nwill\nbe the minimum number of leading spaces among all lines. The parser wont automatically remove the number of indentation spaces in the final output.')
        expected = \
"""Note {
    '''
    The number of spaces you use to indent a block string
    will
    be the minimum number of leading spaces among all lines. The parser wont automatically remove the number of indentation spaces in the final output.
    '''
}"""
        self.assertEqual(note.dbml, expected)

    def test_sql(self) -> None:
        note1 = Note(None)
        self.assertEqual(note1.sql, '')
        note2 = Note('One line of note text')
        self.assertEqual(note2.sql, '-- One line of note text')
        note3 = Note('The number of spaces you use to indent a block string\nwill\nbe the minimum number of leading spaces among all lines. The parser wont automatically remove the number of indentation spaces in the final output.')
        expected = \
"""-- The number of spaces you use to indent a block string
-- will
-- be the minimum number of leading spaces among all lines. The parser wont automatically remove the number of indentation spaces in the final output."""
        self.assertEqual(note3.sql, expected)
