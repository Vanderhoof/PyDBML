import os

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, Mock

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import Index
from pydbml.classes import Expression
from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.classes import Note
from pydbml.schema import Schema
from pydbml import PyDBML


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestGenerateDBML(TestCase):
    def create_schema(self) -> Schema:
        schema = Schema()
        emp_level = Enum(
            'level',
            [
                EnumItem('junior'),
                EnumItem('middle'),
                EnumItem('senior'),
            ]
        )
        schema.add(emp_level)

        t1 = Table('Employees', alias='emp')
        c11 = Column('id', 'integer', pk=True, autoinc=True)
        c12 = Column('name', 'varchar', note=Note('Full employee name'))
        c13 = Column('age', 'number', default=0)
        c14 = Column('level', 'level')
        c15 = Column('favorite_book_id', 'integer')
        t1.add_column(c11)
        t1.add_column(c12)
        t1.add_column(c13)
        t1.add_column(c14)
        t1.add_column(c15)
        schema.add(t1)

        t2 = Table('books')
        c21 = Column('id', 'integer', pk=True, autoinc=True)
        c22 = Column('title', 'varchar')
        c23 = Column('author', 'varchar')
        c24 = Column('country_id', 'integer')
        t2.add_column(c21)
        t2.add_column(c22)
        t2.add_column(c23)
        t2.add_column(c24)
        schema.add(t2)

        t3 = Table('countries')
        c31 = Column('id', 'integer', pk=True, autoinc=True)
        c32 = Column('name', 'varchar2', unique=True)
        t3.add_column(c31)
        t3.add_column(c32)
        i31 = Index([c32], unique=True)
        t3.add_index(i31)
        i32 = Index([Expression('UPPER(name)')])
        t3.add_index(i32)
        schema.add(t3)

        ref1 = Reference('>', c15, c21)
        schema.add(ref1)

        ref2 = Reference('<', c31, c24, name='Country Reference', inline=True)
        schema.add(ref2)

        tg = TableGroup('Unanimate', [t2, t3])
        schema.add(tg)

        p = Project('my project', {'author': 'me', 'reason': 'testing'})
        schema.add(p)
        return schema

    def test_generate_dbml(self) -> None:
        schema = self.create_schema()
        with open(TEST_DATA_PATH / 'integration1.dbml') as f:
            expected = f.read()
        self.assertEqual(schema.dbml, expected)

    def test_generate_sql(self) -> None:
        schema = self.create_schema()
        with open(TEST_DATA_PATH / 'integration1.sql') as f:
            expected = f.read()
        self.assertEqual(schema.sql, expected)

    def test_parser(self):
        source_path = TEST_DATA_PATH / 'integration1.dbml'
        with self.assertRaises(TypeError):
            PyDBML(2)
        res1 = PyDBML(source_path)
        self.assertIsInstance(res1, Schema)
        with open(source_path) as f:
            res2 = PyDBML(f)
        self.assertIsInstance(res2, Schema)
        with open(source_path) as f:
            source = f.read()
        res3 = PyDBML(source)
        self.assertIsInstance(res3, Schema)
        res4 = PyDBML('\ufeff' + source)
        self.assertIsInstance(res4, Schema)

        pydbml = PyDBML()
        self.assertIsInstance(pydbml, PyDBML)
        res5 = pydbml.parse(source)
        self.assertIsInstance(res5, Schema)
        res6 = PyDBML.parse('\ufeff' + source)
        self.assertIsInstance(res6, Schema)
        res7 = PyDBML.parse_file(str(source_path))
        self.assertIsInstance(res7, Schema)
        with open(source_path) as f:
            res8 = PyDBML.parse_file(f)
        self.assertIsInstance(res8, Schema)
