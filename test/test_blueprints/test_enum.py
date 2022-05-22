from unittest import TestCase

from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Note
from pydbml.parser.blueprints import EnumBlueprint
from pydbml.parser.blueprints import EnumItemBlueprint
from pydbml.parser.blueprints import NoteBlueprint


class TestEnumItemBlueprint(TestCase):
    def test_build_minimal(self) -> None:
        bp = EnumItemBlueprint(
            name='Red'
        )
        result = bp.build()
        self.assertIsInstance(result, EnumItem)
        self.assertEqual(result.name, bp.name)

    def test_build_full(self) -> None:
        bp = EnumItemBlueprint(
            name='Red',
            note=NoteBlueprint(text='Note text'),
            comment='Comment text'
        )
        result = bp.build()
        self.assertIsInstance(result, EnumItem)
        self.assertEqual(result.name, bp.name)
        self.assertIsInstance(result.note, Note)
        self.assertEqual(result.note.text, bp.note.text)
        self.assertEqual(result.comment, bp.comment)


class TestEnumBlueprint(TestCase):
    def test_build(self) -> None:
        bp = EnumBlueprint(
            name='Colors',
            items=[
                EnumItemBlueprint(name='Red'),
                EnumItemBlueprint(name='Green'),
                EnumItemBlueprint(name='Blue')
            ],
            comment='Comment text'
        )
        result = bp.build()
        self.assertIsInstance(result, Enum)
        self.assertEqual(result.name, bp.name)
        self.assertEqual(result.comment, bp.comment)
        for ei in result.items:
            self.assertIsInstance(ei, EnumItem)
