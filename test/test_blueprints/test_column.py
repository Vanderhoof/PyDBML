from unittest import TestCase

from pydbml.classes import Note
from pydbml.classes import Column
from pydbml.parser.blueprints import ColumnBlueprint
from pydbml.parser.blueprints import NoteBlueprint


class TestColumn(TestCase):
    def test_build_minimal(self) -> None:
        bp = ColumnBlueprint(
            name='testcol',
            type='varchar'
        )
        result = bp.build()
        self.assertIsInstance(result, Column)
        self.assertEqual(result.name, bp.name)
        self.assertEqual(result.type, bp.type)

    def test_build_full(self) -> None:
        bp = ColumnBlueprint(
            name='id',
            type='number',
            unique=True,
            not_null=True,
            pk=True,
            autoinc=True,
            default=0,
            note=NoteBlueprint(text='note text'),
            comment='Col commment'
        )
        result = bp.build()
        self.assertIsInstance(result, Column)
        self.assertEqual(result.name, bp.name)
        self.assertEqual(result.type, bp.type)
        self.assertEqual(result.unique, bp.unique)
        self.assertEqual(result.not_null, bp.not_null)
        self.assertEqual(result.pk, bp.pk)
        self.assertEqual(result.autoinc, bp.autoinc)
        self.assertEqual(result.default, bp.default)
        self.assertIsInstance(result.note, Note)
        self.assertEqual(result.note.text, bp.note.text)
        self.assertEqual(result.comment, bp.comment)
