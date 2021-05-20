import os

from pathlib import Path
from unittest import TestCase

from pydbml import PyDBML
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import TableNotFoundError


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestParser(TestCase):
    def setUp(self):
        self.results = PyDBML.parse_file(TEST_DATA_PATH / 'general.dbml')

    def test_table_refs(self) -> None:
        p = PyDBML.parse_file(TEST_DATA_PATH / 'general.dbml')
        r = p['order_items'].refs
        self.assertEqual(r[0].col[0].name, 'order_id')
        self.assertEqual(r[0].ref_table.name, 'orders')
        self.assertEqual(r[0].ref_col[0].name, 'id')
        r = p['products'].refs
        self.assertEqual(r[0].col[0].name, 'merchant_id')
        self.assertEqual(r[0].ref_table.name, 'merchants')
        self.assertEqual(r[0].ref_col[0].name, 'id')
        r = p['users'].refs
        self.assertEqual(r[0].col[0].name, 'country_code')
        self.assertEqual(r[0].ref_table.name, 'countries')
        self.assertEqual(r[0].ref_col[0].name, 'code')

    def test_refs(self) -> None:
        p = PyDBML.parse_file(TEST_DATA_PATH / 'general.dbml')
        r = p.refs
        self.assertEqual(r[0].table1.name, 'orders')
        self.assertEqual(r[0].col1[0].name, 'id')
        self.assertEqual(r[0].table2.name, 'order_items')
        self.assertEqual(r[0].col2[0].name, 'order_id')
        self.assertEqual(r[2].table1.name, 'users')
        self.assertEqual(r[2].col1[0].name, 'country_code')
        self.assertEqual(r[2].table2.name, 'countries')
        self.assertEqual(r[2].col2[0].name, 'code')
        self.assertEqual(r[4].table1.name, 'products')
        self.assertEqual(r[4].col1[0].name, 'merchant_id')
        self.assertEqual(r[4].table2.name, 'merchants')
        self.assertEqual(r[4].col2[0].name, 'id')


class TestRefs(TestCase):
    def test_reference_aliases(self):
        results = PyDBML.parse_file(TEST_DATA_PATH / 'relationships_aliases.dbml')
        posts, reviews, users = results['posts'], results['reviews'], results['users']
        posts2, reviews2, users2 = results['posts2'], results['reviews2'], results['users2']

        rs = results.refs
        self.assertEqual(rs[0].table1, users)
        self.assertEqual(rs[0].table2, posts)
        self.assertEqual(rs[1].table1, users)
        self.assertEqual(rs[1].table2, reviews)

        self.assertEqual(rs[2].table1, posts2)
        self.assertEqual(rs[2].table2, users2)
        self.assertEqual(rs[3].table1, reviews2)
        self.assertEqual(rs[3].table2, users2)

    def test_composite_references(self):
        results = PyDBML.parse_file(TEST_DATA_PATH / 'relationships_composite.dbml')
        self.assertEqual(len(results.tables), 4)
        posts, reviews = results['posts'], results['reviews']
        posts2, reviews2 = results['posts2'], results['reviews2']

        rs = results.refs
        self.assertEqual(len(rs), 2)

        self.assertEqual(rs[0].table1, posts)
        self.assertEqual(rs[0].col1, [posts['id'], posts['tag']])
        self.assertEqual(rs[0].table2, reviews)
        self.assertEqual(rs[0].col2, [reviews['post_id'], reviews['tag']])

        self.assertEqual(rs[1].table1, posts2)
        self.assertEqual(rs[1].col1, [posts2['id'], posts2['tag']])
        self.assertEqual(rs[1].table2, reviews2)
        self.assertEqual(rs[1].col2, [reviews2['post_id'], reviews2['tag']])


class TestFaulty(TestCase):
    def test_bad_reference(self) -> None:
        with self.assertRaises(TableNotFoundError):
            PyDBML(TEST_DATA_PATH / 'wrong_inline_ref_table.dbml')
        with self.assertRaises(ColumnNotFoundError):
            PyDBML(TEST_DATA_PATH / 'wrong_inline_ref_column.dbml')

    def test_bad_index(self) -> None:
        with self.assertRaises(ColumnNotFoundError):
            PyDBML(TEST_DATA_PATH / 'wrong_index.dbml')
