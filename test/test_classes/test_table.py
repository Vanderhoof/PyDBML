from unittest import TestCase

import pytest

from pydbml.classes import Column
from pydbml.classes import Expression
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.database import Database
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import IndexNotFoundError
from pydbml.exceptions import UnknownDatabaseError


class TestTable(TestCase):
    def test_schema(self) -> None:
        t = Table('test')
        self.assertEqual(t.schema, 'public')
        t2 = Table('test', 'schema1')
        self.assertEqual(t2.schema, 'schema1')

    def test_getitem(self) -> None:
        t = Table('products')
        c1 = Column('col1', 'integer')
        c2 = Column('col2', 'integer')
        c3 = Column('col3', 'integer')
        t.add_column(c1)
        t.add_column(c2)
        t.add_column(c3)
        self.assertIs(t['col1'], c1)
        self.assertIs(t[1], c2)
        with self.assertRaises(IndexError):
            t[22]
        with self.assertRaises(TypeError):
            t[None]
        with self.assertRaises(ColumnNotFoundError):
            t['wrong']

    def test_init_with_columns(self) -> None:
        t = Table(
            'products',
            columns=(
                Column('col1', 'integer'),
                Column('col2', 'integer'),
                Column('col3', 'integer'),
            )
        )
        self.assertIs(t['col1'].table, t)
        self.assertIs(t['col2'].table, t)
        self.assertIs(t['col3'].table, t)

    def test_init_with_indexes(self) -> None:
        c1 = Column('col1', 'integer')
        c2 = Column('col2', 'integer')
        c3 = Column('col3', 'integer')
        t = Table(
            'products',
            columns=[c1, c2, c3],
            indexes=[Index(subjects=[c1])]
        )
        self.assertIs(t.indexes[0].table, t)

    def test_get(self) -> None:
        t = Table('products')
        c1 = Column('col1', 'integer')
        c2 = Column('col2', 'integer')
        c3 = Column('col3', 'integer')
        t.add_column(c1)
        t.add_column(c2)
        self.assertIs(t.get(0), c1)
        self.assertIs(t.get('col2'), c2)
        self.assertIsNone(t.get('wrong'))
        self.assertIsNone(t.get(22))
        self.assertIs(t.get('wrong', c2), c2)
        self.assertIs(t.get(22, c2), c2)
        self.assertIs(t.get('wrong', c3), c3)

    def test_iter(self) -> None:
        t = Table('products')
        c1 = Column('col1', 'integer')
        c2 = Column('col2', 'integer')
        c3 = Column('col3', 'integer')
        t.add_column(c1)
        t.add_column(c2)
        t.add_column(c3)
        for i1, i2 in zip(t, [c1, c2, c3]):
            self.assertIs(i1, i2)

    def test_add_column(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        self.assertEqual(c1.table, t)
        self.assertEqual(c2.table, t)
        self.assertEqual(t.columns, [c1, c2])
        with self.assertRaises(TypeError):
            t.add_column('wrong type')

    def test_delete_column(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t.delete_column(c1)
        self.assertIsNone(c1.table)
        self.assertNotIn(c1, t.columns)
        t.delete_column(0)
        self.assertIsNone(c2.table)
        self.assertNotIn(c2, t.columns)
        with self.assertRaises(ColumnNotFoundError):
            t.delete_column(c2)

    def test_add_index(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        i1 = Index([c1])
        i2 = Index([c2])
        t.add_column(c1)
        t.add_column(c2)
        t.add_index(i1)
        t.add_index(i2)
        self.assertEqual(i1.table, t)
        self.assertEqual(i2.table, t)
        self.assertEqual(t.indexes, [i1, i2])
        with self.assertRaises(TypeError):
            t.add_index('wrong_type')

    def test_delete_index(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        i1 = Index([c1])
        i2 = Index([c2])
        t.add_column(c1)
        t.add_column(c2)
        t.add_index(i1)
        t.add_index(i2)
        t.delete_index(0)
        self.assertIsNone(i1.table)
        self.assertNotIn(i1, t.indexes)
        t.delete_index(i2)
        self.assertIsNone(i2.table)
        self.assertNotIn(i2, t.indexes)
        with self.assertRaises(IndexNotFoundError):
            t.delete_index(i1)

    def test_get_refs(self):
        t = Table('products')
        with self.assertRaises(UnknownDatabaseError):
            t.get_refs()
        c11 = Column('id', 'integer')
        c12 = Column('name', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names')
        c21 = Column('id', 'integer')
        c22 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        s = Database()
        s.add(t)
        s.add(t2)
        r1 = Reference('>', c12, c22)
        r2 = Reference('-', c11, c21)
        r3 = Reference('<', c11, c22)
        s.add(r1)
        s.add(r2)
        s.add(r3)
        self.assertEqual(t.get_refs(), [r1, r2, r3])
        self.assertEqual(t2.get_refs(), [])

    def test_note_property(self):
        note1 = Note('table note')
        t = Table(name='test')
        t.note = note1
        self.assertIs(t.note.parent, t)


class TestAddIndex:
    @staticmethod
    def test_wrong_type(table1: Table) -> None:
        with pytest.raises(TypeError):
            table1.add_index('wrong_type')


    @staticmethod
    def test_column_not_in_table(table1: Table, table2: Table) -> None:
        with pytest.raises(ColumnNotFoundError):
            table1.add_index(Index([table2.columns[0]]))

    @staticmethod
    def test_ok(table1: Table) -> None:
        i = Index([table1.columns[0]])
        table1.add_index(i)
        assert i.table is table1
