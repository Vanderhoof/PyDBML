from unittest import TestCase
from unittest.mock import Mock

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Note
from pydbml.parser.blueprints import ColumnBlueprint
from pydbml.parser.blueprints import NoteBlueprint
from pydbml.database import Database


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

    def test_enum_type(self) -> None:
        s = Database()
        e = Enum(
            'myenum',
            items=[
                EnumItem('i1'),
                EnumItem('i2')
            ]
        )
        s.add(e)
        parser = Mock()
        parser.database = s

        bp = ColumnBlueprint(
            name='testcol',
            type='myenum'
        )
        bp.parser = parser
        result = bp.build()
        self.assertIs(result.type, e)

    def test_enum_type_schema(self) -> None:
        s = Database()
        e = Enum(
            'myenum',
            schema='myschema',
            items=[
                EnumItem('i1'),
                EnumItem('i2')
            ]
        )
        s.add(e)
        parser = Mock()
        parser.database = s

        bp = ColumnBlueprint(
            name='testcol',
            type='myschema.myenum'
        )
        bp.parser = parser
        result = bp.build()
        self.assertIs(result.type, e)
