from pydbml.classes import Enum
from pydbml.classes import EnumItem
from unittest import TestCase


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

    def test_schema(self) -> None:
        items = [
            EnumItem('created'),
            EnumItem('running'),
            EnumItem('donef'),
            EnumItem('failure'),
        ]
        e = Enum('job_status', items, schema="myschema")
        expected = \
'''CREATE TYPE "myschema"."job_status" AS ENUM (
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

    def test_dbml_schema(self):
        items = [EnumItem('en-US'), EnumItem('ru-RU'), EnumItem('en-GB')]
        e = Enum('lang', items, schema="myschema")
        expected = \
'''Enum "myschema"."lang" {
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

    def test_getitem(self) -> None:
        ei = EnumItem('created')
        items = [
            EnumItem('running'),
            ei,
            EnumItem('donef'),
            EnumItem('failure'),
        ]
        e = Enum('job_status', items)
        self.assertIs(e[1], ei)
        with self.assertRaises(IndexError):
            e[22]
        with self.assertRaises(TypeError):
            e['abc']

    def test_iter(self) -> None:
        ei1 = EnumItem('created')
        ei2 = EnumItem('running')
        ei3 = EnumItem('donef')
        ei4 = EnumItem('failure')
        items = [
            ei1,
            ei2,
            ei3,
            ei4,
        ]
        e = Enum('job_status', items)

        for i1, i2 in zip(e, [ei1, ei2, ei3, ei4]):
            self.assertIs(i1, i2)
