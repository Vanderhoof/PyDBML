from unittest import TestCase
from pydbml.classes import Column
from pydbml.classes import Table
from pydbml.classes import Reference
from pydbml.exceptions import DBMLError


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


class TestReferenceInline(TestCase):
    def test_sql_single(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('>', t, c1, t2, c2, inline=True)

        expected = 'FOREIGN KEY ("name") REFERENCES "names" ("name_val")'
        self.assertEqual(ref.sql, expected)

    def test_sql_reverse(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('<', t, c1, t2, c2, inline=True)

        expected = 'FOREIGN KEY ("name_val") REFERENCES "products" ("name")'
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
        ref = Reference('>', t, [c11, c12], t2, (c21, c22), inline=True)

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
        ref = Reference(
            '>',
            t,
            [c11, c12],
            t2,
            (c21, c22),
            name="country_name",
            comment="Multiline\ncomment for the constraint",
            on_update="CASCADE",
            on_delete="SET NULL",
            inline=True
        )

        expected = \
'''-- Multiline
-- comment for the constraint
CONSTRAINT "country_name" FOREIGN KEY ("name", "country") REFERENCES "names" ("name_val", "country_val") ON UPDATE CASCADE ON DELETE SET NULL'''

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
        ref = Reference('>', t, c2, t2, c21, inline=True)

        expected = 'ref: > "names"."name_val"'
        self.assertEqual(ref.dbml, expected)

    def test_dbml_settings_ignored(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        ref = Reference(
            '<',
            t,
            c2,
            t2,
            c21,
            name='nameref',
            comment='Reference comment\nmultiline',
            on_update='CASCADE',
            on_delete='SET NULL',
            inline=True
        )

        expected = 'ref: < "names"."name_val"'
        self.assertEqual(ref.dbml, expected)

    def test_dbml_composite_inline_ref_forbidden(self):
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
            on_delete='SET NULL',
            inline=True
        )

        with self.assertRaises(DBMLError):
            ref.dbml

