from unittest import TestCase

from pydbml.classes import Note
from pydbml.classes import Project
from pydbml.parser.blueprints import NoteBlueprint
from pydbml.parser.blueprints import ProjectBlueprint


class TestProjectBlueprint(TestCase):
    def test_build_minimal(self) -> None:
        bp = ProjectBlueprint(
            name='MyProject'
        )
        result = bp.build()
        self.assertIsInstance(result, Project)
        self.assertEqual(result.name, bp.name)

    def test_build_full(self) -> None:
        bp = ProjectBlueprint(
            name='MyProject',
            items={
                'author': 'John Wick',
                'nickname': 'Baba Yaga',
                'reason': 'revenge'
            },
            note=NoteBlueprint(text='note text'),
            comment='comment text'
        )
        result = bp.build()
        self.assertIsInstance(result, Project)
        self.assertEqual(result.name, bp.name)
        self.assertEqual(result.items, bp.items)
        self.assertIsNot(result.items, bp.items)
        self.assertIsInstance(result.note, Note)
        self.assertEqual(result.note.text, bp.note.text)
        self.assertEqual(result.comment, bp.comment)
