from unittest import TestCase

from pydbml.classes import Column


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

# TODO: test ref inline
