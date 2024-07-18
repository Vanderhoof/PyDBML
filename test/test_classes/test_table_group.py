from unittest import TestCase

from pydbml.classes import Table
from pydbml.classes import TableGroup


class TestTableGroup(TestCase):
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
