from unittest import TestCase

from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.parser.blueprints import IndexBlueprint
from pydbml.parser.blueprints import NoteBlueprint


class TestIndex(TestCase):
    def test_build_minimal(self) -> None:
        bp = IndexBlueprint(
            subject_names=['a', 'b', 'c']
        )
        result = bp.build()
        self.assertIsInstance(result, Index)
        self.assertEqual(result.subject_names, [])

    def test_build_full(self) -> None:
        bp = IndexBlueprint(
            subject_names=['a', 'b', 'c'],
            name='MyIndex',
            unique=True,
            type='hash',
            pk=True,
            note=NoteBlueprint(text='Note text'),
            comment='Comment text'
        )
        result = bp.build()
        self.assertIsInstance(result, Index)
        self.assertEqual(result.subject_names, [])
        self.assertEqual(result.name, bp.name)
        self.assertEqual(result.unique, bp.unique)
        self.assertEqual(result.type, bp.type)
        self.assertEqual(result.pk, bp.pk)
        self.assertIsInstance(result.note, Note)
        self.assertEqual(result.note.text, bp.note.text)
        self.assertEqual(result.comment, bp.comment)
