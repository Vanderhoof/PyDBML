from pydbml.classes import Table
from pydbml.classes import Index
from pydbml.classes import Column
from unittest import TestCase

from pydbml.classes.sticky_note import StickyNote


class TestNote(TestCase):
    def test_init_types(self):
        n1 = StickyNote('mynote', 'My note text')
        n2 = StickyNote('mynote', 3)
        n3 = StickyNote('mynote', [1, 2, 3])
        n4 = StickyNote('mynote', None)

        self.assertEqual(n1.text, 'My note text')
        self.assertEqual(n2.text, '3')
        self.assertEqual(n3.text, '[1, 2, 3]')
        self.assertEqual(n4.text, '')
        self.assertTrue(n1.name == n2.name == n3.name == n4.name == 'mynote')

    def test_oneline(self):
        note = StickyNote('mynote', 'One line of note text')
        expected = \
'''Note mynote {
    'One line of note text'
}'''
        self.assertEqual(note.dbml, expected)

    def test_forced_multiline(self):
        note = StickyNote('mynote', 'The number of spaces you use to indent a block string\nwill\nbe the minimum number of leading spaces among all lines. The parser wont automatically remove the number of indentation spaces in the final output.')
        expected = \
"""Note mynote {
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
        note = StickyNote('mynote', quotes)
        self.assertEqual(note._prepare_text_for_dbml(), expected)
