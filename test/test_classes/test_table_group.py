from unittest import TestCase

from pydbml.classes import Table
from pydbml.classes import TableGroup


class TestTableGroup(TestCase):
# string items no longer supported
#     def test_dbml(self):
#         tg = TableGroup('mytg', ['merchants', 'countries', 'customers'])
#         expected = \
# '''TableGroup mytg {
#     merchants
#     countries
#     customers
# }'''
#         self.assertEqual(tg.dbml, expected)

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
    "merchants"
    "countries"
    "customers"
}'''
        self.assertEqual(tg.dbml, expected)

    def test_dbml_schema(self):
        merchants = Table('merchants', schema="myschema1")
        countries = Table('countries', schema="myschema2")
        customers = Table('customers', schema="myschema3")
        tg = TableGroup(
            'mytg',
            [merchants, countries, customers],
        )
        expected = \
'''TableGroup mytg {
    "myschema1"."merchants"
    "myschema2"."countries"
    "myschema3"."customers"
}'''
        self.assertEqual(tg.dbml, expected)

    def test_getitem(self) -> None:
        merchants = Table('merchants')
        countries = Table('countries')
        customers = Table('customers')
        tg = TableGroup(
            'mytg',
            [merchants, countries, customers],
            comment='My table group\nmultiline comment'
        )
        self.assertIs(tg[1], countries)
        with self.assertRaises(IndexError):
            tg[22]

    def test_iter(self) -> None:
        merchants = Table('merchants')
        countries = Table('countries')
        customers = Table('customers')
        tg = TableGroup(
            'mytg',
            [merchants, countries, customers],
            comment='My table group\nmultiline comment'
        )
        for i1, i2 in zip(tg, [merchants, countries, customers]):
            self.assertIs(i1, i2)
