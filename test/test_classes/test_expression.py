from unittest import TestCase

from pydbml.classes import Expression


class TestNote(TestCase):
    def test_dbml(self):
        e = Expression('SUM(amount)')
        self.assertEqual(e.dbml, '`SUM(amount)`')
