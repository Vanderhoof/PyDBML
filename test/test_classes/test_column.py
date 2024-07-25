from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Note
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.database import Database
from pydbml.exceptions import TableNotFoundError


class TestColumn(TestCase):
    def test_attributes(self) -> None:
        name = 'name'
        type = 'type'
        unique = True
        not_null = True
        pk = True
        autoinc = True
        default = '1'
        note = Note('note')
        comment = 'comment'
        col = Column(
            name=name,
            type=type,
            unique=unique,
            not_null=not_null,
            pk=pk,
            autoinc=autoinc,
            default=default,
            note=note,
            comment=comment,
        )
        self.assertEqual(col.name, name)
        self.assertEqual(col.type, type)
        self.assertEqual(col.unique, unique)
        self.assertEqual(col.not_null, not_null)
        self.assertEqual(col.pk, pk)
        self.assertEqual(col.autoinc, autoinc)
        self.assertEqual(col.default, default)
        self.assertEqual(col.note.text, note.text)
        self.assertEqual(col.comment, comment)

    def test_database_set(self) -> None:
        col = Column('name', 'int')
        table = Table('name')
        self.assertIsNone(col.database)
        table.add_column(col)
        self.assertIsNone(col.database)
        database = Database()
        database.add(table)
        self.assertIs(col.database, database)

    def test_pk_autoinc(self) -> None:
        r = Column(name='id',
                   type='integer',
                   pk=True,
                   autoinc=True)
        expected = '"id" integer PRIMARY KEY AUTOINCREMENT'
        self.assertEqual(r.sql, expected)

    def test_unique_not_null(self) -> None:
        r = Column(name='id',
                   type='integer',
                   unique=True,
                   not_null=True)
        expected = '"id" integer UNIQUE NOT NULL'
        self.assertEqual(r.sql, expected)

    def test_default(self) -> None:
        r = Column(name='order',
                   type='integer',
                   default=0)
        expected = '"order" integer DEFAULT 0'
        self.assertEqual(r.sql, expected)

    def test_comment(self) -> None:
        r = Column(name='id',
                   type='integer',
                   unique=True,
                   not_null=True,
                   comment="Column comment")
        expected = \
'''-- Column comment
"id" integer UNIQUE NOT NULL'''
        self.assertEqual(r.sql, expected)

    def test_database(self):
        c1 = Column(name='client_id', type='integer')
        t1 = Table(name='products')

        self.assertIsNone(c1.database)
        t1.add_column(c1)
        self.assertIsNone(c1.database)
        s = Database()
        s.add(t1)
        self.assertIs(c1.database, s)

    def test_get_refs(self) -> None:
        c1 = Column(name='client_id', type='integer')
        with self.assertRaises(TableNotFoundError):
            c1.get_refs()
        t1 = Table(name='products')
        t1.add_column(c1)
        c2 = Column(name='id', type='integer', autoinc=True, pk=True)
        t2 = Table(name='clients')
        t2.add_column(c2)

        ref = Reference(type='>', col1=c1, col2=c2, inline=True)
        s = Database()
        s.add(t1)
        s.add(t2)
        s.add(ref)

        self.assertEqual(c1.get_refs(), [ref])

    def test_note_property(self):
        note1 = Note('column note')
        c1 = Column(name='client_id', type='integer')
        c1.note = note1
        self.assertIs(c1.note.parent, c1)


class TestEqual:
    @staticmethod
    def test_other_type() -> None:
        c1 = Column('name', 'VARCHAR2')
        assert c1 != 'name'

    @staticmethod
    def test_different_tables() -> None:
        t1 = Table('table1', columns=[Column('name', 'VARCHAR2')])
        t2 = Table('table2', columns=[Column('name', 'VARCHAR2')])
        assert t1.columns[0] != t2.columns[0]

    @staticmethod
    def test_same_table() -> None:
        t1 = Table('table1', columns=[Column('name', 'VARCHAR2')])
        t2 = Table('table1', columns=[Column('name', 'VARCHAR2')])
        assert t1.columns[0] == t2.columns[0]

    @staticmethod
    def test_same_column() -> None:
        c1 = Column('name', 'VARCHAR2')
        assert c1 == c1

    @staticmethod
    def test_table_not_set() -> None:
        c1 = Column('name', 'VARCHAR2')
        c2 = Column('name', 'VARCHAR2')
        assert c1 == c2

    @staticmethod
    def test_ont_table_not_set() -> None:
        c1 = Column('name', 'VARCHAR2')
        c2 = Column('name', 'VARCHAR2')
        t1 = Table('table1')
        c1.table = t1
        assert c1 != c2

        c1.table, c2.table = None, t1
        assert c1 != c2


def test_repr() -> None:
    c1 = Column('name', 'VARCHAR2')
    assert repr(c1) == "<Column 'name', 'VARCHAR2'>"