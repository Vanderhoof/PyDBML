from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import ReferenceBlueprint
from pydbml.classes import SQLOjbect
from pydbml.classes import Table
from pydbml.classes import TableReference
from pydbml.exceptions import AttributeMissingError
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import DuplicateReferenceError


class TestDBMLObject(TestCase):
    def test_check_attributes_for_sql(self) -> None:
        o = SQLOjbect()
        o.a1 = None
        o.b1 = None
        o.c1 = None
        o.required_attributes = ('a1', 'b1')
        with self.assertRaises(AttributeMissingError):
            o.check_attributes_for_sql()
        o.a1 = 1
        with self.assertRaises(AttributeMissingError):
            o.check_attributes_for_sql()
        o.b1 = 'a2'
        o.check_attributes_for_sql()

    def test_comparison(self) -> None:
        o1 = SQLOjbect()
        o1.a1 = None
        o1.b1 = 'c'
        o1.c1 = 123
        o2 = SQLOjbect()
        o2.a1 = None
        o2.b1 = 'c'
        o2.c1 = 123
        self.assertTrue(o1 == o2)
        o1.a2 = True
        self.assertFalse(o1 == o2)


# class TestReferenceBlueprint(TestCase):
#     def test_basic_sql(self) -> None:
#         r = ReferenceBlueprint(
#             ReferenceBlueprint.MANY_TO_ONE,
#             table1='bookings',
#             col1='country',
#             table2='ids',
#             col2='id'
#         )
#         expected = 'ALTER TABLE "bookings" ADD FOREIGN KEY ("country") REFERENCES "ids ("id");'
#         self.assertEqual(r.sql, expected)
#         r.type = ReferenceBlueprint.ONE_TO_ONE
#         self.assertEqual(r.sql, expected)
#         r.type = ReferenceBlueprint.ONE_TO_MANY
#         expected2 = 'ALTER TABLE "ids" ADD FOREIGN KEY ("id") REFERENCES "bookings ("country");'
#         self.assertEqual(r.sql, expected2)

#     def test_full(self) -> None:
#         r = ReferenceBlueprint(
#             ReferenceBlueprint.MANY_TO_ONE,
#             name='refname',
#             table1='bookings',
#             col1='country',
#             table2='ids',
#             col2='id',
#             on_update='cascade',
#             on_delete='restrict'
#         )
#         expected = 'ALTER TABLE "bookings" ADD CONSTRAINT "refname" FOREIGN KEY ("country") REFERENCES "ids ("id") ON UPDATE CASCADE ON DELETE RESTRICT;'
#         self.assertEqual(r.sql, expected)
#         r.type = ReferenceBlueprint.ONE_TO_ONE
#         self.assertEqual(r.sql, expected)
#         r.type = ReferenceBlueprint.ONE_TO_MANY
#         expected2 = 'ALTER TABLE "ids" ADD CONSTRAINT "refname" FOREIGN KEY ("id") REFERENCES "bookings ("country") ON UPDATE CASCADE ON DELETE RESTRICT;'
#         self.assertEqual(r.sql, expected2)


# class TestTableReference(TestCase):
#     def test_basic_sql(self) -> None:
#         r = TableReference(col='order_id',
#                            ref_table='orders',
#                            ref_col='id')
#         expected = 'FOREIGN KEY ("order_id") REFERENCES "orders ("id")'
#         self.assertEqual(r.sql, expected)

#     def test_full(self) -> None:
#         r = TableReference(col='order_id',
#                            ref_table='orders',
#                            ref_col='id',
#                            name='refname',
#                            on_delete='set null',
#                            on_update='no action')
#         expected = 'CONSTRAINT "refname" FOREIGN KEY ("order_id") REFERENCES "orders ("id") ON UPDATE NO ACTION ON DELETE SET NULL'
#         self.assertEqual(r.sql, expected)


class TestColumn(TestCase):
    def test_basic_sql(self) -> None:
        r = Column(name='id',
                   type_='integer')
        expected = '"id" integer'
        self.assertEqual(r.sql, expected)

    def test_note(self) -> None:
        n = Note('Column note')
        r = Column(name='id',
                   type_='integer',
                   note=n)
        expected = '"id" integer -- Column note'
        self.assertEqual(r.sql, expected)

    def test_pk_autoinc(self) -> None:
        r = Column(name='id',
                   type_='integer',
                   pk=True,
                   autoinc=True)
        expected = '"id" integer PRIMARY KEY AUTOINCREMENT'
        self.assertEqual(r.sql, expected)

    def test_unique_not_null(self) -> None:
        r = Column(name='id',
                   type_='integer',
                   unique=True,
                   not_null=True)
        expected = '"id" integer UNIQUE NOT NULL'
        self.assertEqual(r.sql, expected)

    def test_default(self) -> None:
        r = Column(name='order',
                   type_='integer',
                   default=0)
        expected = '"order" integer DEFAULT 0'
        self.assertEqual(r.sql, expected)

    def test_table_setter(self) -> None:
        r1 = ReferenceBlueprint(
            ReferenceBlueprint.MANY_TO_ONE,
            name='refname',
            table1='bookings',
            col1='order_id',
            table2='orders',
            col2='order',
        )
        r2 = ReferenceBlueprint(
            ReferenceBlueprint.MANY_TO_ONE,
            name='refname',
            table1='purchases',
            col1='order_id',
            table2='orders',
            col2='order',
        )
        c = Column(
            name='order',
            type_='integer',
            default=0,
            ref_blueprints=[r1, r2]
        )
        t = Table('orders')
        c.table = t
        self.assertEqual(c.table, t)
        self.assertEqual(c.ref_blueprints[0].table1, t.name)
        self.assertEqual(c.ref_blueprints[1].table1, t.name)


class TestIndex(TestCase):
    def test_basic_sql(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subject_names=['id'],
                  table=t)
        t.add_index(r)
        expected = 'CREATE INDEX ON "products" ("id");'
        self.assertEqual(r.sql, expected)

    def test_note(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        n = Note('Index note')
        r = Index(subject_names=['id'],
                  table=t,
                  note=n)
        t.add_index(r)
        expected = 'CREATE INDEX ON "products" ("id"); -- Index note'
        self.assertEqual(r.sql, expected)

    def test_unique_type_composite(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        t.add_column(Column('name', 'varchar'))
        r = Index(subject_names=['id', 'name'],
                  table=t,
                  type_='hash',
                  unique=True)
        t.add_index(r)
        expected = 'CREATE UNIQUE INDEX ON "products" USING HASH ("id", "name");'
        self.assertEqual(r.sql, expected)

    def test_pk(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        t.add_column(Column('name', 'varchar'))
        r = Index(subject_names=['id', 'name'],
                  table=t,
                  pk=True)
        t.add_index(r)
        expected = 'PRIMARY KEY ("id", "name")'
        self.assertEqual(r.sql, expected)

    def test_composite_with_expression(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subject_names=['id', '(id*3)'],
                  table=t)
        t.add_index(r)
        self.assertEqual(r.subjects, [t['id'], '(id*3)'])
        expected = 'CREATE INDEX ON "products" ("id", (id*3));'
        self.assertEqual(r.sql, expected)


class TestTable(TestCase):
    def test_one_column(self) -> None:
        t = Table('products')
        c = Column('id', 'integer')
        t.add_column(c)
        expected = 'CREATE TABLE "products" (\n  "id" integer\n);\n'
        self.assertEqual(t.sql, expected)

    def test_ref(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        r = TableReference(c2, t2, c21)
        t.add_ref(r)
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  FOREIGN KEY ("name") REFERENCES "names ("name_val")
);
'''
        self.assertEqual(t.sql, expected)

    def test_duplicate_ref(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        r1 = TableReference(c2, t2, c21)
        t.add_ref(r1)
        r2 = TableReference(c2, t2, c21)
        self.assertEqual(r1, r2)
        with self.assertRaises(DuplicateReferenceError):
            t.add_ref(r2)

    def test_note(self) -> None:
        n = Note('Table note')
        t = Table('products', note=n)
        c = Column('id', 'integer')
        t.add_column(c)
        expected = 'CREATE TABLE "products" (\n  -- Table note\n  "id" integer\n);\n'
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
        r = TableReference(c2, t2, c21)
        t.add_ref(r)
        i = Index(['id', 'name'])
        t.add_index(i)
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  FOREIGN KEY ("name") REFERENCES "names ("name_val")
);

CREATE INDEX ON "products" ("id", "name");
'''
        self.assertEqual(t.sql, expected)

    def test_index_inline(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        i = Index(['id', 'name'], pk=True)
        t.add_index(i)
        expected = \
'''CREATE TABLE "products" (
  "id" integer,
  "name" varchar2,
  PRIMARY KEY ("id", "name")
);
'''
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

    def test_add_index(self) -> None:
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        i1 = Index(['id'])
        i2 = Index(['name'])
        t.add_column(c1)
        t.add_column(c2)
        t.add_index(i1)
        t.add_index(i2)
        self.assertEqual(i1.table, t)
        self.assertEqual(i2.table, t)
        self.assertEqual(t.indexes, [i1, i2])

    def test_add_bad_index(self) -> None:
        t = Table('products')
        c = Column('id', 'integer')
        i = Index(['id', 'name'])
        t.add_column(c)
        with self.assertRaises(ColumnNotFoundError):
            t.add_index(i)


class TestEnum(TestCase):
    def test_simple_enum(self) -> None:
        items = [
            EnumItem('created'),
            EnumItem('running'),
            EnumItem('donef'),
            EnumItem('failure'),
        ]
        e = Enum('job_status', items)
        expected = \
'''CREATE TYPE "job_status" AS ENUM (
  'created',
  'running',
  'donef',
  'failure',
);'''
        self.assertEqual(e.sql, expected)

    def test_notes(self) -> None:
        n = Note('EnumItem note')
        items = [
            EnumItem('created', note=n),
            EnumItem('running'),
            EnumItem('donef', note=n),
            EnumItem('failure'),
        ]
        e = Enum('job_status', items)
        expected = \
'''CREATE TYPE "job_status" AS ENUM (
  'created', -- EnumItem note
  'running',
  'donef', -- EnumItem note
  'failure',
);'''
        self.assertEqual(e.sql, expected)
