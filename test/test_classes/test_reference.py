from unittest import TestCase

from pydbml.classes import Column
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.exceptions import DBMLError
from pydbml.exceptions import TableNotFoundError


class TestReference(TestCase):
    def test_table1(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('>', c1, c2)
        self.assertIsNone(ref.table1)
        t.add_column(c1)
        self.assertIs(ref.table1, t)

    def test_join_table(self) -> None:
        t1 = Table('books')
        c11 = Column('id', 'integer', pk=True)
        c12 = Column('author', 'varchar')
        t1.add_column(c11)
        t1.add_column(c12)
        t2 = Table('authors')
        c21 = Column('id', 'integer', pk=True)
        c22 = Column('name', 'varchar')
        t2.add_column(c21)
        t2.add_column(c22)
        ref0 = Reference('>', [c11], [c21])
        ref = Reference('<>', [c11, c12], [c21, c22])

        self.assertIsNone(ref0.join_table)
        self.assertEqual(ref.join_table.name, 'books_authors')
        self.assertEqual(len(ref.join_table.columns), 4)

    def test_join_table_none(self) -> None:
        t1 = Table('books')
        c11 = Column('id', 'integer', pk=True)
        c12 = Column('author', 'varchar')
        t1.add_column(c11)
        t1.add_column(c12)
        t2 = Table('authors')
        c21 = Column('id', 'integer', pk=True)
        c22 = Column('name', 'varchar')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = Reference('<>', [c11], [c21])

        _table1 = ref.table1
        ref.col1[0].table = None
        with self.assertRaises(TableNotFoundError):
            ref.join_table

        ref.col1[0].table = _table1
        ref.col2[0].table = None
        with self.assertRaises(TableNotFoundError):
            ref.join_table

    def test_dbml_simple(self):
        t = Table('products')
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        ref = Reference('>', c2, c21)

        expected = \
'''Ref {
    "products"."name" > "names"."name_val"
}'''
        self.assertEqual(ref.dbml, expected)

    def test_dbml_schema(self):
        t = Table('products', schema="myschema1")
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names', schema="myschema2")
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        ref = Reference('>', c2, c21)

        expected = \
'''Ref {
    "myschema1"."products"."name" > "myschema2"."names"."name_val"
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
        t2 = Table('names', schema="myschema")
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = Reference(
            '<',
            [c2, c3],
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
    "products".("name", "country") < "myschema"."names".("name_val", "country") [update: CASCADE, delete: SET NULL]
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
        ref = Reference('>', c1, c2, inline=True)

        expected = 'FOREIGN KEY ("name") REFERENCES "names" ("name_val")'
        self.assertEqual(ref.sql, expected)

    def test_sql_schema_single(self):
        t = Table('products', schema="myschema1")
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names', schema="myschema2")
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('>', c1, c2, inline=True)

        expected = 'FOREIGN KEY ("name") REFERENCES "myschema2"."names" ("name_val")'
        self.assertEqual(ref.sql, expected)

    def test_sql_reverse(self):
        t = Table('products')
        c1 = Column('name', 'varchar2')
        t.add_column(c1)
        t2 = Table('names')
        c2 = Column('name_val', 'varchar2')
        t2.add_column(c2)
        ref = Reference('<', c1, c2, inline=True)

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
        ref = Reference('>', [c11, c12], (c21, c22), inline=True)

        expected = 'FOREIGN KEY ("name", "country") REFERENCES "names" ("name_val", "country_val")'
        self.assertEqual(ref.sql, expected)

    def test_sql_schema_multiple(self):
        t = Table('products', schema="myschema1")
        c11 = Column('name', 'varchar2')
        c12 = Column('country', 'varchar2')
        t.add_column(c11)
        t.add_column(c12)
        t2 = Table('names', schema="myschema2")
        c21 = Column('name_val', 'varchar2')
        c22 = Column('country_val', 'varchar2')
        t2.add_column(c21)
        t2.add_column(c22)
        ref = Reference('<', [c11, c12], (c21, c22), inline=True)

        expected = 'FOREIGN KEY ("name_val", "country_val") REFERENCES "myschema1"."products" ("name", "country")'
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
            [c11, c12],
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
        ref = Reference('>', c2, c21, inline=True)

        expected = 'ref: > "names"."name_val"'
        self.assertEqual(ref.dbml, expected)

    def test_dbml_schema(self):
        t = Table('products', schema="myschema1")
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        t.add_column(c1)
        t.add_column(c2)
        t2 = Table('names', schema="myschema2")
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        ref = Reference('>', c2, c21, inline=True)

        expected = 'ref: > "myschema2"."names"."name_val"'
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
            c2,
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
            [c2, c3],
            (c21, c22),
            name='nameref',
            comment='Reference comment\nmultiline',
            on_update='CASCADE',
            on_delete='SET NULL',
            inline=True
        )

        with self.assertRaises(DBMLError):
            ref.dbml

    def test_validate_different_tables(self):
        t1 = Table('products')
        c11 = Column('id', 'integer')
        c12 = Column('name', 'varchar2')
        t1.add_column(c11)
        t1.add_column(c12)
        t2 = Table('names')
        c21 = Column('name_val', 'varchar2')
        t2.add_column(c21)
        ref = Reference(
            '<',
            [c12, c21],
            [c21],
            name='nameref',
            comment='Reference comment\nmultiline',
            on_update='CASCADE',
            on_delete='SET NULL',
            inline=True
        )
        with self.assertRaises(DBMLError):
            ref._validate()

        ref = Reference(
            '<',
            [c11, c12],
            [c21, c12],
            name='nameref',
            comment='Reference comment\nmultiline',
            on_update='CASCADE',
            on_delete='SET NULL',
            inline=True
        )
        with self.assertRaises(DBMLError):
            ref._validate()

    def test_validate_no_table(self):
        c1 = Column('id', 'integer')
        c2 = Column('name', 'varchar2')
        c3 = Column('age', 'number')
        c4 = Column('active', 'boolean')
        ref1 = Reference(
            '<',
            c1,
            c2
        )
        with self.assertRaises(TableNotFoundError):
            ref1._validate_for_sql()
        table = Table('name')
        table.add_column(c1)
        with self.assertRaises(TableNotFoundError):
            ref1._validate_for_sql()
        table.delete_column(c1)

        ref2 = Reference(
            '<',
            [c1, c2],
            [c3, c4]
        )
        with self.assertRaises(TableNotFoundError):
            ref2._validate_for_sql()
        table = Table('name')
        table.add_column(c1)
        table.add_column(c2)
        with self.assertRaises(TableNotFoundError):
            ref2._validate_for_sql()
