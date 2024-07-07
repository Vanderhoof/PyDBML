from pydbml.classes import Note
from pydbml.classes import Table
from pydbml.classes import Index
from pydbml.classes import Column
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

    def test_prepare_text_for_dbml(self):
        quotes = "'asd' There's ''' asda ''''  asd ''''' asdsa ''"
        expected = "\\'asd\\' There\\'s \\''' asda \\'''\\'  asd \\'''\\'\\' asdsa \\'\\'"
        note = Note(quotes)
        self.assertEqual(note._prepare_text_for_dbml(), expected)

    def test_escaped_newline_sql(self) -> None:
        note = Note('One line of note text \\\nstill one line')
        self.assertEqual(note.sql, '-- One line of note text still one line')
