from pydbml.classes import Project
from pydbml.classes import Note

from unittest import TestCase


class TestProject(TestCase):
    def test_note_property(self):
        note1 = Note('column note')
        p = Project('myproject')
        p.note = note1
        self.assertIs(p.note.parent, p)
