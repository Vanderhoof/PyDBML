from unittest import TestCase

from pydbml.classes import Note
from pydbml.parser.blueprints import NoteBlueprint


class TestNote(TestCase):
    def test_build(self) -> None:
        bp = NoteBlueprint(text='Note text')
        result = bp.build()
        self.assertIsInstance(result, Note)
        self.assertEqual(result.text, bp.text)
