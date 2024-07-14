from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Table


class TestIndex(TestCase):
    def test_note_property(self):
        note1 = Note('column note')
        t = Table('products')
        c = Column('id', 'integer')
        i = Index(subjects=[c])
        i.note = note1
        self.assertIs(i.note.parent, i)
