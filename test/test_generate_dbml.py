import os

from pathlib import Path
from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import Index
from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.classes import Note
from pydbml.exceptions import SchemaValidationError
from pydbml.schema import Schema


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestGenerateDBML(TestCase):
    def test_generate_dbml(self) -> None:
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
        i31 = Index([c32])
        t3.add_index(i31)
        # TODO: expression class
        # i32 = Index([''])
        schema.add(t3)

        ref1 = Reference('>', c15, c21)
        schema.add(ref1)

        ref2 = Reference('<', c31, c24, name='Country Reference')
        schema.add(ref2)

