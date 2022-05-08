from unittest import TestCase

from pydbml.classes import Index
from pydbml.classes import Table
from pydbml.classes import Column


class TestIndex(TestCase):
    def test_basic_sql(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subjects=[t.columns[0]])
        t.add_index(r)
        self.assertIs(r.table, t)
        expected = 'CREATE INDEX ON "products" ("id");'
        self.assertEqual(r.sql, expected)

    def test_comment(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subjects=[t.columns[0]],
                  comment='Index comment')
        t.add_index(r)
        self.assertIs(r.table, t)
        expected = \
'''-- Index comment
CREATE INDEX ON "products" ("id");'''

        self.assertEqual(r.sql, expected)

    def test_unique_type_composite(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        t.add_column(Column('name', 'varchar'))
        r = Index(
            subjects=[
                t.columns[0],
                t.columns[1]
            ],
            type_='hash',
            unique=True
        )
        t.add_index(r)
        expected = 'CREATE UNIQUE INDEX ON "products" USING HASH ("id", "name");'
        self.assertEqual(r.sql, expected)

    def test_pk(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        t.add_column(Column('name', 'varchar'))
        r = Index(
            subjects=[
                t.columns[0],
                t.columns[1]
            ],
            pk=True
        )
        t.add_index(r)
        expected = 'PRIMARY KEY ("id", "name")'
        self.assertEqual(r.sql, expected)

    def test_composite_with_expression(self) -> None:
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        r = Index(subjects=[t.columns[0], '(id*3)'])
        t.add_index(r)
        self.assertEqual(r.subjects, [t['id'], '(id*3)'])
        expected = 'CREATE INDEX ON "products" ("id", (id*3));'
        self.assertEqual(r.sql, expected)

    def test_dbml_simple(self):
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        i = Index(subjects=[t.columns[0]])
        t.add_index(i)

        expected = 'id'
        self.assertEqual(i.dbml, expected)

    def test_dbml_composite(self):
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        i = Index(subjects=[t.columns[0], '(id*3)'])
        t.add_index(i)

        expected = '(id, `id*3`)'
        self.assertEqual(i.dbml, expected)

    def test_dbml_full(self):
        t = Table('products')
        t.add_column(Column('id', 'integer'))
        i = Index(
            subjects=[t.columns[0], '(getdate())'],
            name='Dated id',
            unique=True,
            type_='hash',
            pk=True,
            note='Note on the column',
            comment='Comment on the index'
        )
        t.add_index(i)
        expected = \
'''// Comment on the index
(id, `getdate()`) [name: 'Dated id', pk, unique, type: hash, note: 'Note on the column']'''
        self.assertEqual(i.dbml, expected)
