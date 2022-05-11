import os

from pathlib import Path
from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Index
from pydbml.classes import Table
from pydbml.schema import Schema


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestCreateTable(TestCase):
    def test_one_column(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        self.assertEqual(c.table, t)
        schema = Schema()
        schema.add(t)
        self.assertEqual(t.schema, schema)
        self.assertEqual(schema.tables[0], t)
        self.assertEqual(schema.tables[0].name, 'test_table')
        self.assertEqual(schema.tables[0].columns[0].name, 'test')

    def test_delete_column(self) -> None:
        c1 = Column('col1', 'varchar', True)
        c2 = Column('col2', 'number', False)
        t = Table('test_table')
        t.add_column(c1)
        t.add_column(c2)
        result = t.delete_column(1)
        self.assertEqual(result, c2)
        self.assertIsNone(result.table)

    def test_delete_table(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        schema = Schema()
        schema.add(t)
        self.assertEqual(t.schema, schema)
        self.assertEqual(schema.tables[0], t)
        schema.delete(t)
        self.assertIsNone(t.schema)
        self.assertEqual(schema.tables, [])


class TestCreateIndex(TestCase):
    def test_simple_index(self):
        c1 = Column('col1', 'varchar', True)
        c2 = Column('col2', 'number', False)
        t = Table('test_table')
        t.add_column(c1)
        t.add_column(c2)
        i = Index([c1], 'IndexName', True)
        self.assertIsNone(i.table)
        t.add_index(i)
        self.assertEqual(i.table, t)

    def test_complex_index(self):
        c1 = Column('col1', 'varchar', True)
        c2 = Column('col2', 'number', False)
        t = Table('test_table')
        t.add_column(c1)
        t.add_column(c2)
        i1 = Index([c1, c2], 'Compound', True)
        self.assertIsNone(i1.table)
        t.add_index(i1)
        self.assertEqual(i1.table, t)
        i2 = Index([c1, '(c2 * 3)'], 'Compound expression', True)
        self.assertIsNone(i2.table)
        t.add_index(i2)
        self.assertEqual(i2.table, t)

    def test_delete_index(self):
        c1 = Column('col1', 'varchar', True)
        c2 = Column('col2', 'number', False)
        t = Table('test_table')
        t.add_column(c1)
        t.add_column(c2)
        i = Index([c1], 'IndexName', True)
        self.assertIsNone(i.table)
        t.add_index(i)
        self.assertEqual(i.table, t)
        t.delete_index(0)
        self.assertIsNone(i.table)
        self.assertEqual(t.indexes, [])
