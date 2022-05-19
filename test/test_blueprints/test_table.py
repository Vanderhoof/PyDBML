from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Expression
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Table
from pydbml.exceptions import ColumnNotFoundError
from pydbml.parser.blueprints import ColumnBlueprint
from pydbml.parser.blueprints import ExpressionBlueprint
from pydbml.parser.blueprints import IndexBlueprint
from pydbml.parser.blueprints import NoteBlueprint
from pydbml.parser.blueprints import ReferenceBlueprint
from pydbml.parser.blueprints import TableBlueprint


class TestTable(TestCase):
    def test_build_minimal(self) -> None:
        bp = TableBlueprint(name='TestTable')
        result = bp.build()
        self.assertIsInstance(result, Table)
        self.assertEqual(result.name, bp.name)

    def test_build_full_simple(self) -> None:
        bp = TableBlueprint(
            name='TestTable',
            alias='TestAlias',
            note=NoteBlueprint(text='Note text'),
            header_color='#ccc',
            comment='comment text'
        )
        result = bp.build()
        self.assertIsInstance(result, Table)
        self.assertEqual(result.name, bp.name)
        self.assertEqual(result.alias, bp.alias)
        self.assertIsInstance(result.note, Note)
        self.assertEqual(result.note.text, bp.note.text)
        self.assertEqual(result.header_color, bp.header_color)
        self.assertEqual(result.comment, bp.comment)

    def test_with_columns(self) -> None:
        bp = TableBlueprint(
            name='TestTable',
            columns=[
                ColumnBlueprint(name='id', type='Integer', not_null=True, autoinc=True),
                ColumnBlueprint(name='name', type='Varchar')
            ]
        )
        result = bp.build()
        self.assertIsInstance(result, Table)
        self.assertEqual(result.name, bp.name)
        for col in result.columns:
            self.assertIsInstance(col, Column)

    def test_with_indexes(self) -> None:
        bp = TableBlueprint(
            name='TestTable',
            columns=[
                ColumnBlueprint(name='id', type='Integer', not_null=True, autoinc=True),
                ColumnBlueprint(name='name', type='Varchar')
            ],
            indexes=[
                IndexBlueprint(subject_names=['name', 'id'], unique=True),
                IndexBlueprint(subject_names=['id', ExpressionBlueprint('name*2')], name='ExprIndex')
            ]
        )
        result = bp.build()
        self.assertIsInstance(result, Table)
        self.assertEqual(result.name, bp.name)
        for col in result.columns:
            self.assertIsInstance(col, Column)
        for ind in result.indexes:
            self.assertIsInstance(ind, Index)
        self.assertIsInstance(result.indexes[1].subjects[1], Expression)

    def test_bad_index(self) -> None:
        bp = TableBlueprint(
            name='TestTable',
            columns=[
                ColumnBlueprint(name='id', type='Integer', not_null=True, autoinc=True),
                ColumnBlueprint(name='name', type='Varchar')
            ],
            indexes=[
                IndexBlueprint(subject_names=['name', 'id'], unique=True),
                IndexBlueprint(subject_names=['wrong', '(name*2)'], name='ExprIndex')
            ]
        )
        with self.assertRaises(ColumnNotFoundError):
            bp.build()

    def test_get_reference_blueprints(self) -> None:
        bp = TableBlueprint(
            name='TestTable',
            columns=[
                ColumnBlueprint(
                    name='id',
                    type='Integer',
                    not_null=True,
                    autoinc=True,
                    ref_blueprints=[
                        ReferenceBlueprint(
                            type='<',
                            inline=True,
                            table2='AnotherTable',
                            col2=['AnotherCol'])
                    ]
                ),
                ColumnBlueprint(
                    name='name',
                    type='Varchar',
                    ref_blueprints=[
                        ReferenceBlueprint(
                            type='>',
                            inline=True,
                            table2='YetAnotherTable',
                            col2=['YetAnotherCol'])
                    ]
                )
            ]
        )
        result = bp.build()
        self.assertIsInstance(result, Table)
        self.assertEqual(result.name, bp.name)
        ref_bps = bp.get_reference_blueprints()
        self.assertEqual(ref_bps[0].table1, result.name)
        self.assertEqual(ref_bps[0].col1, 'id')
        self.assertEqual(ref_bps[1].table1, result.name)
        self.assertEqual(ref_bps[1].col1, 'name')
