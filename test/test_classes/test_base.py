from unittest import TestCase

from pydbml.classes.base import SQLOjbect
from pydbml.exceptions import AttributeMissingError


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
