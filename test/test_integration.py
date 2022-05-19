import os

from pathlib import Path
from unittest import TestCase

from pydbml import PyDBML
from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Expression
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.database import Database


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestGenerateDBML(TestCase):
    def create_database(self) -> Database:
        database = Database()
        emp_level = Enum(
            'level',
            [
                EnumItem('junior'),
                EnumItem('middle'),
                EnumItem('senior'),
            ]
        )
        database.add(emp_level)

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
        database.add(t1)

        t2 = Table('books')
        c21 = Column('id', 'integer', pk=True, autoinc=True)
        c22 = Column('title', 'varchar')
        c23 = Column('author', 'varchar')
        c24 = Column('country_id', 'integer')
        t2.add_column(c21)
        t2.add_column(c22)
        t2.add_column(c23)
        t2.add_column(c24)
        database.add(t2)

        t3 = Table('countries')
        c31 = Column('id', 'integer', pk=True, autoinc=True)
        c32 = Column('name', 'varchar2', unique=True)
        t3.add_column(c31)
        t3.add_column(c32)
        i31 = Index([c32], unique=True)
        t3.add_index(i31)
        i32 = Index([Expression('UPPER(name)')])
        t3.add_index(i32)
        database.add(t3)

        ref1 = Reference('>', c15, c21)
        database.add(ref1)

        ref2 = Reference('<', c31, c24, name='Country Reference', inline=True)
        database.add(ref2)

        tg = TableGroup('Unanimate', [t2, t3])
        database.add(tg)

        p = Project('my project', {'author': 'me', 'reason': 'testing'})
        database.add(p)
        return database

    def test_generate_dbml(self) -> None:
        database = self.create_database()
        with open(TEST_DATA_PATH / 'integration1.dbml') as f:
            expected = f.read()
        self.assertEqual(database.dbml, expected)

    def test_generate_sql(self) -> None:
        database = self.create_database()
        with open(TEST_DATA_PATH / 'integration1.sql') as f:
            expected = f.read()
        self.assertEqual(database.sql, expected)

    def test_parser(self):
        source_path = TEST_DATA_PATH / 'integration1.dbml'
        with self.assertRaises(TypeError):
            PyDBML(2)
        res1 = PyDBML(source_path)
        self.assertIsInstance(res1, Database)
        with open(source_path) as f:
            res2 = PyDBML(f)
        self.assertIsInstance(res2, Database)
        with open(source_path) as f:
            source = f.read()
        res3 = PyDBML(source)
        self.assertIsInstance(res3, Database)
        res4 = PyDBML('\ufeff' + source)
        self.assertIsInstance(res4, Database)

        pydbml = PyDBML()
        self.assertIsInstance(pydbml, PyDBML)
        res5 = pydbml.parse(source)
        self.assertIsInstance(res5, Database)
        res6 = PyDBML.parse('\ufeff' + source)
        self.assertIsInstance(res6, Database)
        res7 = PyDBML.parse_file(str(source_path))
        self.assertIsInstance(res7, Database)
        with open(source_path) as f:
            res8 = PyDBML.parse_file(f)
        self.assertIsInstance(res8, Database)
