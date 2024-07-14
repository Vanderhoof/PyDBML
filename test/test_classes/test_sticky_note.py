from unittest import TestCase

from pydbml._classes.sticky_note import StickyNote


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
