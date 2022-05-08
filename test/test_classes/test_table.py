from unittest import TestCase

from pydbml.classes import Index
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.classes import Column


class TestTable(TestCase):
    def test_one_column(self) -> None:
        t = Table('products')
        c = Column('id', 'integer')
        t.add_column(c)
        expected = 'CREATE TABLE "products" (\n  "id" integer\n);'
        self.assertEqual(t.sql, expected)

#     def test_ref(self) -> None:
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         t2 = Table('names')
#         c21 = Column('name_val', 'varchar2')
#         t2.add_column(c21)
#         r = TableReference(c2, t2, c21)
#         t.add_ref(r)
#         expected = \
# '''CREATE TABLE "products" (
#   "id" integer,
#   "name" varchar2,
#   FOREIGN KEY ("name") REFERENCES "names" ("name_val")
# );'''
#         self.assertEqual(t.sql, expected)

#     def test_duplicate_ref(self) -> None:
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         t2 = Table('names')
#         c21 = Column('name_val', 'varchar2')
#         t2.add_column(c21)
#         r1 = TableReference(c2, t2, c21)
#         t.add_ref(r1)
#         r2 = TableReference(c2, t2, c21)
#         self.assertEqual(r1, r2)
#         with self.assertRaises(DuplicateReferenceError):
#             t.add_ref(r2)

#     def test_notes(self) -> None:
#         n = Note('Table note')
#         nc1 = Note('First column note')
#         nc2 = Note('Another column\nmultiline note')
#         t = Table('products', note=n)
#         c1 = Column('id', 'integer', note=nc1)
#         c2 = Column('name', 'varchar')
#         c3 = Column('country', 'varchar', note=nc2)
#         t.add_column(c1)
#         t.add_column(c2)
#         t.add_column(c3)
#         expected = \
# '''CREATE TABLE "products" (
#   "id" integer,
#   "name" varchar,
#   "country" varchar
# );

# COMMENT ON TABLE "products" IS 'Table note';

# COMMENT ON COLUMN "products"."id" IS 'First column note';

# COMMENT ON COLUMN "products"."country" IS 'Another column
# multiline note';'''
#         self.assertEqual(t.sql, expected)

#     def test_ref_index(self) -> None:
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         t2 = Table('names')
#         c21 = Column('name_val', 'varchar2')
#         t2.add_column(c21)
#         r = TableReference(c2, t2, c21)
#         t.add_ref(r)
#         i = Index(['id', 'name'])
#         t.add_index(i)
#         expected = \
# '''CREATE TABLE "products" (
#   "id" integer,
#   "name" varchar2,
#   FOREIGN KEY ("name") REFERENCES "names" ("name_val")
# );

# CREATE INDEX ON "products" ("id", "name");'''
#         self.assertEqual(t.sql, expected)

#     def test_index_inline(self) -> None:
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         i = Index(['id', 'name'], pk=True)
#         t.add_index(i)
#         expected = \
# '''CREATE TABLE "products" (
#   "id" integer,
#   "name" varchar2,
#   PRIMARY KEY ("id", "name")
# );'''
#         self.assertEqual(t.sql, expected)

#     def test_index_inline_and_comments(self) -> None:
#         t = Table('products', comment='Multiline\ntable comment')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         i = Index(['id', 'name'], pk=True, comment='Multiline\nindex comment')
#         t.add_index(i)
#         expected = \
# '''-- Multiline
# -- table comment
# CREATE TABLE "products" (
#   "id" integer,
#   "name" varchar2,
#   -- Multiline
#   -- index comment
#   PRIMARY KEY ("id", "name")
# );'''
#         self.assertEqual(t.sql, expected)

#     def test_add_column(self) -> None:
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         self.assertEqual(c1.table, t)
#         self.assertEqual(c2.table, t)
#         self.assertEqual(t.columns, [c1, c2])

#     def test_add_index(self) -> None:
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         i1 = Index(['id'])
#         i2 = Index(['name'])
#         t.add_column(c1)
#         t.add_column(c2)
#         t.add_index(i1)
#         t.add_index(i2)
#         self.assertEqual(i1.table, t)
#         self.assertEqual(i2.table, t)
#         self.assertEqual(t.indexes, [i1, i2])

#     def test_add_bad_index(self) -> None:
#         t = Table('products')
#         c = Column('id', 'integer')
#         i = Index(['id', 'name'])
#         t.add_column(c)
#         with self.assertRaises(ColumnNotFoundError):
#             t.add_index(i)

#     def test_dbml_simple(self):
#         t = Table('products')
#         c1 = Column('id', 'integer')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c1)
#         t.add_column(c2)
#         expected = \
# '''Table "products" {
#     "id" integer
#     "name" varchar2
# }'''
#         self.assertEqual(t.dbml, expected)

#     def test_dbml_full(self):
#         t = Table(
#             'products',
#             alias='pd',
#             note='My multiline\nnote',
#             comment='My multiline\ncomment'
#         )
#         c0 = Column('zero', 'number')
#         c1 = Column('id', 'integer', unique=True, note='Multiline\ncomment note')
#         c2 = Column('name', 'varchar2')
#         t.add_column(c0)
#         t.add_column(c1)
#         t.add_column(c2)
#         i1 = Index(['zero', 'id'], unique=True)
#         i2 = Index(['(capitalize(name))'], comment="index comment")
#         t.add_index(i1)
#         t.add_index(i2)
#         expected = \
# """// My multiline
# // comment
# Table "products" as "pd" {
#     "zero" number
#     "id" integer [unique, note: '''Multiline
#     comment note''']
#     "name" varchar2
#     Note {
#         '''
#         My multiline
#         note
#         '''
#     }

#     indexes {
#         (zero, id) [unique]
#         // index comment
#         `capitalize(name)`
#     }
# }"""
#         self.assertEqual(t.dbml, expected)
