import os

from pathlib import Path
from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.database import Database
from pydbml.exceptions import DatabaseValidationError


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestDatabase(TestCase):
    def test_add_table(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        database = Database()
        res = database.add_table(t)
        self.assertEqual(t.database, database)
        self.assertIs(res, t)
        self.assertIn(t, database.tables)

    def test_add_table_alias(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table', alias='myalias')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        self.assertIsInstance(t.alias, str)
        self.assertIs(database[t.alias], t)

    def test_add_table_alias_bad(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test', alias='myalias')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        t2 = Table('test_table', alias='myalias')
        with self.assertRaises(DatabaseValidationError):
            database.add_table(t2)
        self.assertIsNone(t2.database)

    def test_add_table_bad(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        with self.assertRaises(DatabaseValidationError):
            database.add_table(t)
        t2 = Table('test_table')
        with self.assertRaises(DatabaseValidationError):
            database.add_table(t2)

    def test_delete_table(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table', alias='myalias')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        res = database.delete_table(t)
        self.assertIsNone(t.database, database)
        self.assertIs(res, t)
        self.assertNotIn(t, database.tables)
        self.assertNotIn('test_table', database.table_dict)
        self.assertNotIn('myalias', database.table_dict)

    def test_delete_missing_table(self) -> None:
        t = Table('test_table')
        database = Database()
        with self.assertRaises(DatabaseValidationError):
            database.delete_table(t)
        self.assertIsNone(t.database, database)

    def test_add_reference(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        database.add_table(t2)
        ref = Reference('>', c, c2)
        res = database.add_reference(ref)
        self.assertEqual(ref.database, database)
        self.assertIs(res, ref)
        self.assertIn(ref, database.refs)

    def test_add_reference_bad(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        database.add_table(t2)
        ref = Reference('>', c, c2)
        database.add_reference(ref)
        with self.assertRaises(DatabaseValidationError):
            database.add_reference(ref)

        c3 = Column('test', 'varchar', True)
        t3 = Table('test_table')
        t3.add_column(c3)
        database3 = Database()
        database3.add_table(t3)
        c32 = Column('test2', 'integer')
        t32 = Table('test_table2')
        t32.add_column(c32)
        database3.add_table(t32)
        ref3 = Reference('>', c3, c32)
        with self.assertRaises(DatabaseValidationError):
            database.add_reference(ref3)

    def test_delete_reference(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        database.add_table(t2)
        ref = Reference('>', c, c2)
        res = database.add_reference(ref)
        res = database.delete_reference(ref)
        self.assertIsNone(ref.database, database)
        self.assertIs(res, ref)
        self.assertNotIn(ref, database.refs)

    def test_delete_missing_reference(self) -> None:
        c = Column('test', 'varchar', True)
        t = Table('test_table')
        t.add_column(c)
        database = Database()
        database.add_table(t)
        c2 = Column('test2', 'integer')
        t2 = Table('test_table2')
        t2.add_column(c2)
        database.add_table(t2)
        ref = Reference('>', c, c2)
        with self.assertRaises(DatabaseValidationError):
            database.delete_reference(ref)
        self.assertIsNone(ref.database)

    def test_add_enum(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        database = Database()
        res = database.add_enum(e)
        self.assertEqual(e.database, database)
        self.assertIs(res, e)
        self.assertIn(e, database.enums)

    def test_add_enum_bad(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        database = Database()
        database.add_enum(e)
        with self.assertRaises(DatabaseValidationError):
            database.add_enum(e)
        e2 = Enum('myenum', [EnumItem('a2'), EnumItem('b2')])
        with self.assertRaises(DatabaseValidationError):
            database.add_enum(e2)

    def test_delete_enum(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        database = Database()
        database.add_enum(e)
        res = database.delete_enum(e)
        self.assertIsNone(e.database)
        self.assertIs(res, e)
        self.assertNotIn(e, database.enums)

    def test_delete_missing_enum(self) -> None:
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        database = Database()
        with self.assertRaises(DatabaseValidationError):
            database.delete_enum(e)
        self.assertIsNone(e.database)

    def test_add_table_group(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        database = Database()
        res = database.add_table_group(tg)
        self.assertEqual(tg.database, database)
        self.assertIs(res, tg)
        self.assertIn(tg, database.table_groups)

    def test_add_table_group_bad(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        database = Database()
        database.add_table_group(tg)
        with self.assertRaises(DatabaseValidationError):
            database.add_table_group(tg)
        tg2 = TableGroup('mytablegroup', [t2])
        with self.assertRaises(DatabaseValidationError):
            database.add_table_group(tg2)

    def test_delete_table_group(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        database = Database()
        database.add_table_group(tg)
        res = database.delete_table_group(tg)
        self.assertIsNone(tg.database)
        self.assertIs(res, tg)
        self.assertNotIn(tg, database.table_groups)

    def test_delete_missing_table_group(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        database = Database()
        with self.assertRaises(DatabaseValidationError):
            database.delete_table_group(tg)
        self.assertIsNone(tg.database)

    def test_add_project(self) -> None:
        p = Project('myproject')
        database = Database()
        res = database.add_project(p)
        self.assertEqual(p.database, database)
        self.assertIs(res, p)
        self.assertIs(database.project, p)

    def test_add_another_project(self) -> None:
        p = Project('myproject')
        database = Database()
        database.add_project(p)
        p2 = Project('anotherproject')
        res = database.add_project(p2)
        self.assertEqual(p2.database, database)
        self.assertIs(res, p2)
        self.assertIs(database.project, p2)
        self.assertIsNone(p.database)

    def test_delete_project(self) -> None:
        p = Project('myproject')
        database = Database()
        database.add_project(p)
        res = database.delete_project()
        self.assertIsNone(p.database, database)
        self.assertIs(res, p)
        self.assertIsNone(database.project)

    def test_delete_missing_project(self) -> None:
        database = Database()
        with self.assertRaises(DatabaseValidationError):
            database.delete_project()

    def test_geititem(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2', schema='myschema')
        database = Database()
        database.add_table(t1)
        database.add_table(t2)
        self.assertIs(database['public.table1'], t1)
        self.assertIs(database['myschema.table2'], t2)
        self.assertIs(database[0], t1)
        self.assertIs(database[1], t2)
        with self.assertRaises(TypeError):
            database[None]
        with self.assertRaises(IndexError):
            database[2]
        with self.assertRaises(KeyError):
            database['wrong']

    def test_iter(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        database = Database()
        database.add_table(t1)
        database.add_table(t2)
        self.assertEqual(list(iter(database)), [t1, t2])

    def test_add(self) -> None:
        t1 = Table('table1')
        t2 = Table('table2')
        tg = TableGroup('mytablegroup', [t1, t2])
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        database = Database()
        database.add(t1)
        database.add(t2)
        database.add(e)
        database.add(tg)
        self.assertIs(t1.database, database)
        self.assertIs(t2.database, database)
        self.assertIs(e.database, database)
        self.assertIs(tg.database, database)
        self.assertIn(t1, database.tables)
        self.assertIn(t2, database.tables)
        self.assertIn(tg, database.table_groups)
        self.assertIn(e, database.enums)

    def test_add_bad(self) -> None:
        class Test:
            pass
        t = Test()
        database = Database()
        with self.assertRaises(DatabaseValidationError):
            database.add(t)
        with self.assertRaises(AttributeError):
            t.database

    def test_delete(self) -> None:
        t1 = Table('table1')
        c1 = Column('col1', 'int')
        t1.add_column(c1)
        t2 = Table('table2')
        c2 = Column('col2', 'int')
        t2.add_column(c2)
        ref = Reference('>', [c1], [c2])
        tg = TableGroup('mytablegroup', [t1, t2])
        e = Enum('myenum', [EnumItem('a'), EnumItem('b')])
        p = Project('myproject')
        database = Database()
        database.add(t1)
        database.add(t2)
        database.add(e)
        database.add(tg)
        database.add(ref)
        database.add(p)

        database.delete(t1)
        database.delete(t2)
        database.delete(e)
        database.delete(tg)
        database.delete(ref)
        database.delete(p)
        self.assertIsNone(t1.database)
        self.assertIsNone(t2.database)
        self.assertIsNone(e.database)
        self.assertIsNone(tg.database)
        self.assertIsNone(ref.database)
        self.assertIsNone(p.database)
        self.assertIsNone(database.project)
        self.assertNotIn(t1, database.tables)
        self.assertNotIn(t2, database.tables)
        self.assertNotIn(tg, database.table_groups)
        self.assertNotIn(e, database.enums)
        self.assertNotIn(ref, database.refs)

    def test_delete_bad(self) -> None:
        class Test:
            pass
        t = Test()
        database = Database()
        with self.assertRaises(DatabaseValidationError):
            database.delete(t)
        with self.assertRaises(AttributeError):
            t.database
