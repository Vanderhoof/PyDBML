from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import IndexNotFoundError
from pydbml.exceptions import UnknownSchemaError
from pydbml.schema import Schema


class TestTable(TestCase):
    def test_one_column(self) -> None:
        t = Table('products')
        c = Column('id', 'integer')
        t.add_column(c)
        s = Schema()
        s.add(t)
        expected = 'CREATE TABLE "products" (\n  "id" integer\n);'
        self.assertEqual(t.sql, expected)

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

    def test_ref(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        s = Schema()
        s.add(t)
        s.add(t2)
        r = Reference('>', c2, c21)
        s.add(r)
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2
);'''
        self.assertEqual(t.sql, expected)
        r.inline = True
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  FOREIGN KEY ("name") REFERENCES "names" ("name_val")
);'''
        self.assertEqual(t.sql, expected)

    def test_notes(self) -> None:
        n = Note('Table note')
        nc1 = Note('First column note')
        nc2 = Note('Another column\nmultiline note')
        t = Table('products', note=n)
        c1 = Column('id', 'integer', note=nc1)
        c2 = Column('name', 'varchar')
        c3 = Column('country', 'varchar', note=nc2)
        t.add_column(c1)
        t.add_column(c2)
        t.add_column(c3)
        s = Schema()
        s.add(t)
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar,
  "country" varchar
);

COMMENT ON TABLE "products" IS 'Table note';

COMMENT ON COLUMN "products"."id" IS 'First column note';

COMMENT ON COLUMN "products"."country" IS 'Another column
multiline note';'''
        self.assertEqual(t.sql, expected)

    def test_ref_index(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        s = Schema()
        s.add(t)

        r = Reference('>', c2, c21, inline=True)
        s.add(r)
        i = Index(subjects=[c1, c2])
        t.add_index(i)
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  FOREIGN KEY ("name") REFERENCES "names" ("name_val")
);

CREATE INDEX ON "products" ("id", "name");'''
        self.assertEqual(t.sql, expected)

    def test_index_inline(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        i = Index(subjects=[c1, c2], pk=True)
        t.add_index(i)
        s = Schema()
        s.add(t)

        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  PRIMARY KEY ("id", "name")
);'''
        self.assertEqual(t.sql, expected)

    def test_index_inline_and_comments(self) -> None:
        t = Table('products', comment='Multiline\ntable comment')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        i = Index(subjects=[c1, c2], pk=True, comment='Multiline\nindex comment')
        t.add_index(i)
        s = Schema()
        s.add(t)

        expected = \
'''-- Multiline
-- table comment
CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  -- Multiline
  -- index comment
  PRIMARY KEY ("id", "name")
);'''
        self.assertEqual(t.sql, expected)

    def test_add_column(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        self.assertEqual(c1.table, t)
        self.assertEqual(c2.table, t)
        self.assertEqual(t.columns, [c1, c2])

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

    def test_get_references_for_sql(self):
        t = Table('products')
        with self.assertRaises(UnknownSchemaError):
            t._get_references_for_sql()
        c11 = Column('id', 'integer')
        c12 = Column('name', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names')
        c21 = Column('id', 'integer')
        c22 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        s = Schema()
        s.add(t)
        s.add(t2)
        r1 = Reference('>', c12, c22)
        r2 = Reference('-', c11, c21)
        r3 = Reference('<', c11, c22)
        s.add(r1)
        s.add(r2)
        s.add(r3)
        self.assertEqual(t._get_references_for_sql(), [])
        self.assertEqual(t2._get_references_for_sql(), [])
        r1.inline = r2.inline = r3.inline = True
        self.assertEqual(t._get_references_for_sql(), [r1, r2])
        self.assertEqual(t2._get_references_for_sql(), [r3])

    def test_get_refs(self):
        t = Table('products')
        with self.assertRaises(UnknownSchemaError):
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
        s = Schema()
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

    def test_dbml_simple(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        s = Schema()
        s.add(t)

        expected = \
'''Table "products" {
    "id" integer
    "name" varchar2
}'''
        self.assertEqual(t.dbml, expected)

    def test_dbml_reference(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        s = Schema()
        s.add(t)
        s.add(t2)
        r = Reference('>', c2, c21)
        s.add(r)
        expected = \
'''Table "products" {
    "id" integer
    "name" varchar2
}'''
        self.assertEqual(t.dbml, expected)
        r.inline = True
        expected = \
'''Table "products" {
    "id" integer
    "name" varchar2 [ref: > "names"."name_val"]
}'''
        self.assertEqual(t.dbml, expected)
        expected = \
'''Table "names" {
    "name_val" varchar2
}'''
        self.assertEqual(t2.dbml, expected)

    def test_dbml_full(self):
        t = Table(
            'products',
            alias='pd',
            note='My multiline\nnote',
            comment='My multiline\ncomment'
        )
        c0 = Column('zero', 'number')
        c1 = Column('id', 'integer', unique=True, note='Multiline\ncomment note')
        c2 = Column('name', 'varchar2')
        t.add_column(c0)
        t.add_column(c1)
        t.add_column(c2)
        i1 = Index(['zero', 'id'], unique=True)
        i2 = Index(['(capitalize(name))'], comment="index comment")
        t.add_index(i1)
        t.add_index(i2)
        s = Schema()
        s.add(t)

        expected = \
"""// My multiline
// comment
Table "products" as "pd" {
    "zero" number
    "id" integer [unique, note: '''Multiline
    comment note''']
    "name" varchar2
    Note {
        '''
        My multiline
        note
        '''
    }

    indexes {
        (zero, id) [unique]
        // index comment
        `capitalize(name)`
    }
}"""
        self.assertEqual(t.dbml, expected)
