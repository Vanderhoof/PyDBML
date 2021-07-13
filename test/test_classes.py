from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import TableReference
from pydbml.classes import ReferenceBlueprint
from pydbml.classes import SQLOjbect
from pydbml.classes import Table
from pydbml.classes import TableGroup
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

    def test_comment(self) -> None:
        r = Column(name='id',
                   type_='integer',
                   unique=True,
                   not_null=True,
                   comment="Column comment")
        expected = \
'''-- Column comment
"id" integer UNIQUE NOT NULL'''
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

    def test_dbml_simple(self):
        c = Column(
            name='order',
            type_='integer'
        )
        expected = '"order" integer'

        self.assertEqual(c.dbml, expected)

    def test_dbml_full(self):
        c = Column(
            name='order',
            type_='integer',
            unique=True,
            not_null=True,
            pk=True,
            autoinc=True,
            default='Def_value',
            note='Note on the column',
            comment='Comment on the column'
        )
        expected = \
'''// Comment on the column
"order" integer [pk, increment, default: 'Def_value', unique, not null, note: 'Note on the column']'''

        self.assertEqual(c.dbml, expected)

    def test_dbml_multiline_note(self):
        c = Column(
            name='order',
            type_='integer',
            not_null=True,
            note='Note on the column\nmultiline',
            comment='Comment on the column'
        )
        expected = \
"""// Comment on the column
"order" integer [not null, note: '''Note on the column
multiline''']"""

        self.assertEqual(c.dbml, expected)

    def test_dbml_default(self):
        c = Column(
            name='order',
            type_='integer',
            default='String value'
        )
        expected = "\"order\" integer [default: 'String value']"
        self.assertEqual(c.dbml, expected)

        c.default = 3
        expected = '"order" integer [default: 3]'
        self.assertEqual(c.dbml, expected)

        c.default = 3.33
        expected = '"order" integer [default: 3.33]'
        self.assertEqual(c.dbml, expected)

        c.default = "(now() - interval '5 days')"
        expected = "\"order\" integer [default: `now() - interval '5 days'`]"
        self.assertEqual(c.dbml, expected)

        c.default = 'NULL'
        expected = '"order" integer [default: null]'
        self.assertEqual(c.dbml, expected)

        c.default = 'TRue'
        expected = '"order" integer [default: true]'
        self.assertEqual(c.dbml, expected)

        c.default = 'false'
        expected = '"order" integer [default: false]'
        self.assertEqual(c.dbml, expected)

class TestIndex(TestCase):
    def test_basic_sql(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subject_names=['id'],
                  table=t)
        t.add_index(r)
        expected = 'CREATE INDEX ON "products" ("id");'
        self.assertEqual(r.sql, expected)

    def test_comment(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subject_names=['id'],
                  table=t,
                  comment='Index comment')
        t.add_index(r)
        expected = \
'''-- Index comment
CREATE INDEX ON "products" ("id");'''

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

    def test_dbml_simple(self):
        i = Index(
            ['id']
        )

        expected = 'id'
        self.assertEqual(i.dbml, expected)

    def test_dbml_composite(self):
        i = Index(
            ['id', '(id*3)']
        )

        expected = '(id, `id*3`)'
        self.assertEqual(i.dbml, expected)

    def test_dbml_full(self):
        i = Index(
            ['id', '(getdate())'],
            name='Dated id',
            unique=True,
            type_='hash',
            pk=True,
            note='Note on the column',
            comment='Comment on the index'
        )
        expected = \
'''// Comment on the index
(id, `getdate()`) [name: 'Dated id', pk, unique, type: hash, note: 'Note on the column']'''


class TestTable(TestCase):
    def test_one_column(self) -> None:
        t = Table('products')
        c = Column('id', 'integer')
        t.add_column(c)
        expected = 'CREATE TABLE "products" (\n  "id" integer\n);'
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
  FOREIGN KEY ("name") REFERENCES "names" ("name_val")
);'''
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
        r = TableReference(c2, t2, c21)
        t.add_ref(r)
        i = Index(['id', 'name'])
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
        i = Index(['id', 'name'], pk=True)
        t.add_index(i)
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
        i = Index(['id', 'name'], pk=True, comment='Multiline\nindex comment')
        t.add_index(i)
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

    def test_dbml_simple(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        expected = \
'''Table "products" {
    "id" integer
    "name" varchar2
}'''
        self.assertEqual(t.dbml, expected)

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

class TestEnumItem(TestCase):
    def test_dbml_simple(self):
        ei = EnumItem('en-US')
        expected = '"en-US"'
        self.assertEqual(ei.dbml, expected)

    def test_sql(self):
        ei = EnumItem('en-US')
        expected = "'en-US',"
        self.assertEqual(ei.sql, expected)

    def test_dbml_full(self):
        ei = EnumItem('en-US', note='preferred', comment='EnumItem comment')
        expected = \
'''// EnumItem comment
"en-US" [note: 'preferred']'''
        self.assertEqual(ei.dbml, expected)


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

    def test_comments(self) -> None:
        items = [
            EnumItem('created', comment='EnumItem comment'),
            EnumItem('running'),
            EnumItem('donef', comment='EnumItem\nmultiline comment'),
            EnumItem('failure'),
        ]
        e = Enum('job_status', items, comment='Enum comment')
        expected = \
'''-- Enum comment
CREATE TYPE "job_status" AS ENUM (
  -- EnumItem comment
  'created',
  'running',
  -- EnumItem
  -- multiline comment
  'donef',
  'failure',
);'''
        self.assertEqual(e.sql, expected)

    def test_dbml_simple(self):
        items = [EnumItem('en-US'), EnumItem('ru-RU'), EnumItem('en-GB')]
        e = Enum('lang', items)
        expected = \
'''Enum "lang" {
    "en-US"
    "ru-RU"
    "en-GB"
}'''
        self.assertEqual(e.dbml, expected)

    def test_dbml_full(self):
        items = [
            EnumItem('en-US', note='preferred'),
            EnumItem('ru-RU', comment='Multiline\ncomment'),
            EnumItem('en-GB')]
        e = Enum('lang', items, comment="Enum comment")
        expected = \
'''// Enum comment
Enum "lang" {
    "en-US" [note: 'preferred']
    // Multiline
    // comment
    "ru-RU"
    "en-GB"
}'''
        self.assertEqual(e.dbml, expected)



class TestTableReference(TestCase):
    def test_sql_single(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = TableReference(
            c1, t2, c2)

        expected = 'FOREIGN KEY ("name") REFERENCES "names" ("name_val")'
        self.assertEqual(ref.sql, expected)

    def test_sql_multiple(self):
        t = Table('products')
        c11 = Column('name', 'varchar2')
        c12 = Column('country', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = TableReference(
            [c11, c12],
            t2,
            (c21, c22)
        )

        expected = 'FOREIGN KEY ("name", "country") REFERENCES "names" ("name_val", "country_val")'
        self.assertEqual(ref.sql, expected)

    def test_sql_full(self):
        t = Table('products')
        c11 = Column('name', 'varchar2')
        c12 = Column('country', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = TableReference(
            [c11, c12],
            t2,
            (c21, c22),
            name="country_name",
            on_delete='SET NULL',
            on_update='CASCADE'
        )

        expected = 'CONSTRAINT "country_name" FOREIGN KEY ("name", "country") REFERENCES "names" ("name_val", "country_val") ON UPDATE CASCADE ON DELETE SET NULL'
        self.assertEqual(ref.sql, expected)

class TestReference(TestCase):
    def test_sql_single(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('>', t, c1, t2, c2)

        expected = 'ALTER TABLE "products" ADD FOREIGN KEY ("name") REFERENCES "names" ("name_val");'
        self.assertEqual(ref.sql, expected)

    def test_sql_reverse(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('<', t, c1, t2, c2)

        expected = 'ALTER TABLE "names" ADD FOREIGN KEY ("name_val") REFERENCES "products" ("name");'
        self.assertEqual(ref.sql, expected)

    def test_sql_multiple(self):
        t = Table('products')
        c11 = Column('name', 'varchar2')
        c12 = Column('country', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = Reference('>', t, [c11, c12], t2, (c21, c22))

        expected = 'ALTER TABLE "products" ADD FOREIGN KEY ("name", "country") REFERENCES "names" ("name_val", "country_val");'
        self.assertEqual(ref.sql, expected)

    def test_sql_full(self):
        t = Table('products')
        c11 = Column('name', 'varchar2')
        c12 = Column('country', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = Reference(
            '>',
            t,
            [c11, c12],
            t2,
            (c21, c22),
            name="country_name",
            comment="Multiline\ncomment for the constraint",
            on_update="CASCADE",
            on_delete="SET NULL"
        )

        expected = \
'''-- Multiline
-- comment for the constraint
ALTER TABLE "products" ADD CONSTRAINT "country_name" FOREIGN KEY ("name", "country") REFERENCES "names" ("name_val", "country_val") ON UPDATE CASCADE ON DELETE SET NULL;'''

        self.assertEqual(ref.sql, expected)

    def test_dbml_simple(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        ref = Reference('>', t, c2, t2, c21)

        expected = \
'''Ref {
    "products"."name" > "names"."name_val"
}'''
        self.assertEqual(ref.dbml, expected)

    def test_dbml_full(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        c3 = Column('country', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t.add_column(c3)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = Reference(
            '<',
            t,
            [c2, c3],
            t2,
            (c21, c22),
            name='nameref',
            comment='Reference comment\nmultiline',
            on_update='CASCADE',
            on_delete='SET NULL'
        )

        expected = \
'''// Reference comment
// multiline
Ref nameref {
    "products".("name", "country") < "names".("name_val", "country") [update: CASCADE, delete: SET NULL]
}'''
        self.assertEqual(ref.dbml, expected)


class TestNote(TestCase):
    def test_init_types(self):
        n1 = Note('My note text')
        n2 = Note(3)
        n3 = Note([1, 2, 3])
        n4 = Note(None)
        n5 = Note(n1)

        self.assertEqual(n1.text, 'My note text')
        self.assertEqual(n2.text, '3')
        self.assertEqual(n3.text, '[1, 2, 3]')
        self.assertEqual(n4.text, '')
        self.assertEqual(n5.text, 'My note text')

    def test_oneline(self):
        note = Note('One line of note text')
        expected = \
'''Note {
    'One line of note text'
}'''
        self.assertEqual(note.dbml, expected)

    def test_multiline(self):
        note = Note('The number of spaces you use to indent a block string will be the minimum number of leading spaces among all lines. The parser will automatically remove the number of indentation spaces in the final output.')
        expected = \
"""Note {
    '''
    The number of spaces you use to indent a block string will be the minimum number 
    of leading spaces among all lines. The parser will automatically remove the number 
    of indentation spaces in the final output.
    '''
}"""
        self.assertEqual(note.dbml, expected)


    def test_forced_multiline(self):
        note = Note('The number of spaces you use to indent a block string\nwill\nbe the minimum number of leading spaces among all lines. The parser will automatically remove the number of indentation spaces in the final output.')
        expected = \
"""Note {
    '''
    The number of spaces you use to indent a block string
    will
    be the minimum number of leading spaces among all lines. The parser will automatically 
    remove the number of indentation spaces in the final output.
    '''
}"""
        self.assertEqual(note.dbml, expected)


class TestTableGroup(TestCase):
    def test_dbml(self):
        tg = TableGroup('mytg', ['merchants', 'countries', 'customers'])
        expected = \
'''TableGroup mytg {
    merchants
    countries
    customers
}'''
        self.assertEqual(tg.dbml, expected)

    def test_dbml_with_comment_and_real_tables(self):
        merchants = Table('merchants')
        countries = Table('countries')
        customers = Table('customers')
        tg = TableGroup(
            'mytg',
            [merchants, countries, customers],
            comment='My table group\nmultiline comment'
        )
        expected = \
'''// My table group
// multiline comment
TableGroup mytg {
    merchants
    countries
    customers
}'''
        self.assertEqual(tg.dbml, expected)

class TestProject(TestCase):
    def test_dbml_note(self):
        p = Project('myproject', note='Project note')
        expected = \
'''Project myproject {
    Note {
        'Project note'
    }
}'''
        self.assertEqual(p.dbml, expected)

    def test_dbml_full(self):
        p = Project(
            'myproject',
            items={
                'database_type': 'PostgreSQL',
                'story': "One day I was eating my cantaloupe and\nI thought, why shouldn't I?\nWhy shouldn't I create a database?"
            },
            comment='Multiline\nProject comment',
            note='Multiline\nProject note')
        expected = \
"""// Multiline
// Project comment
Project myproject {
    database_type: 'PostgreSQL'
    story: '''One day I was eating my cantaloupe and
    I thought, why shouldn't I?
    Why shouldn't I create a database?'''
    Note {
        '''
        Multiline
        Project note
        '''
    }
}"""
        self.assertEqual(p.dbml, expected)
