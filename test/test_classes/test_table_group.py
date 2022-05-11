from unittest import TestCase

from pydbml.classes import Table
from pydbml.classes import TableGroup


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
