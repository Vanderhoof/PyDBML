import os

from pathlib import Path
from unittest import TestCase

from pydbml import PyDBML
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import TableNotFoundError
from pydbml.parser.parser import PyDBMLParser


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestParser(TestCase):
    def setUp(self):
        self.results = PyDBML.parse_file(TEST_DATA_PATH / 'general.dbml')

    def test_table_refs(self) -> None:
        p = PyDBML.parse_file(TEST_DATA_PATH / 'general.dbml')
        r = p['public.orders'].get_refs()
        self.assertEqual(r[0].col2[0].name, 'order_id')
        self.assertEqual(r[0].col1[0].table.name, 'orders')
        self.assertEqual(r[0].col1[0].name, 'id')
        r = p['public.products'].get_refs()
        self.assertEqual(r[1].col1[0].name, 'merchant_id')
        self.assertEqual(r[1].col2[0].table.name, 'merchants')
        self.assertEqual(r[1].col2[0].name, 'id')
        r = p['public.users'].get_refs()
        self.assertEqual(r[0].col1[0].name, 'country_code')
        self.assertEqual(r[0].col2[0].table.name, 'countries')
        self.assertEqual(r[0].col2[0].name, 'code')

    def test_refs(self) -> None:
        p = PyDBML.parse_file(TEST_DATA_PATH / 'general.dbml')
        r = p.refs
        self.assertEqual(r[0].col1[0].table.name, 'orders')
        self.assertEqual(r[0].col1[0].name, 'id')
        self.assertEqual(r[0].col2[0].table.name, 'order_items')
        self.assertEqual(r[0].col2[0].name, 'order_id')
        self.assertEqual(r[2].col1[0].table.name, 'users')
        self.assertEqual(r[2].col1[0].name, 'country_code')
        self.assertEqual(r[2].col2[0].table.name, 'countries')
        self.assertEqual(r[2].col2[0].name, 'code')
        self.assertEqual(r[4].col1[0].table.name, 'products')
        self.assertEqual(r[4].col1[0].name, 'merchant_id')
        self.assertEqual(r[4].col2[0].table.name, 'merchants')
        self.assertEqual(r[4].col2[0].name, 'id')

    def test_inline_refs_schema(self) -> None:
        # Thanks @jens-koster for this example
        source = '''
Table core.pk_tbl {
    pk_col varchar [pk]
}
Table core.fk_tbl {
    fk_col varchar [ref: > core.pk_tbl.pk_col]
}
'''
        p = PyDBMLParser(source)
        p.parse()
        r = p.refs
        pk_tbl = p.tables[0]
        fk_tble = p.tables[1]
        ref = p.refs[0]
        self.assertEqual(ref.table1, fk_tble.name)
        self.assertEqual(ref.table2, pk_tbl.name)
        self.assertEqual(ref.schema1, fk_tble.schema)
        self.assertEqual(ref.schema2, pk_tbl.schema)


class TestRefs(TestCase):
    def test_reference_aliases(self):
        results = PyDBML.parse_file(TEST_DATA_PATH / 'relationships_aliases.dbml')
        posts, reviews, users = results['public.posts'], results['public.reviews'], results['public.users']
        posts2, reviews2, users2 = results['public.posts2'], results['public.reviews2'], results['public.users2']

        rs = results.refs
        self.assertEqual(rs[0].col1[0].table, users)
        self.assertEqual(rs[0].col2[0].table, posts)
        self.assertEqual(rs[1].col1[0].table, users)
        self.assertEqual(rs[1].col2[0].table, reviews)

        self.assertEqual(rs[2].col1[0].table, posts2)
        self.assertEqual(rs[2].col2[0].table, users2)
        self.assertEqual(rs[3].col1[0].table, reviews2)
        self.assertEqual(rs[3].col2[0].table, users2)

    def test_composite_references(self):
        results = PyDBML.parse_file(TEST_DATA_PATH / 'relationships_composite.dbml')
        self.assertEqual(len(results.tables), 4)
        posts, reviews = results['public.posts'], results['public.reviews']
        posts2, reviews2 = results['public.posts2'], results['public.reviews2']

        rs = results.refs
        self.assertEqual(len(rs), 2)

        self.assertEqual(rs[0].col1[0].table, posts)
        self.assertEqual(rs[0].col1, [posts['id'], posts['tag']])
        self.assertEqual(rs[0].col2[0].table, reviews)
        self.assertEqual(rs[0].col2, [reviews['post_id'], reviews['tag']])

        self.assertEqual(rs[1].col1[0].table, posts2)
        self.assertEqual(rs[1].col1, [posts2['id'], posts2['tag']])
        self.assertEqual(rs[1].col2[0].table, reviews2)
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


class TestPyDBMLParser(TestCase):
    def test_edge(self) -> None:
        p = PyDBMLParser('')
        with self.assertRaises(RuntimeError):
            p.locate_table('myschema', 'test')
        with self.assertRaises(RuntimeError):
            p.parse_blueprint(1, 1, [1])


class TestNotesIdempotent(TestCase):
    def test_note_is_idempotent(self):
        dbml_source = """
Table test {
    id integer
    Note {
        '''
        Indented note which is actually a Markdown formatted string:
        
        - List item 1
        - Another list item
        
        ```python
        def test():
              print('Hello world!')
              return 1
        ```
        '''
    }
}
"""
        source_text = \
"""Indented note which is actually a Markdown formatted string:

- List item 1
- Another list item

```python
def test():
      print('Hello world!')
      return 1
```"""
        p = PyDBML(dbml_source)
        note = p.tables[0].note
        self.assertEqual(source_text, note.text)

        p_mod = p
        for _ in range(10):
            p_mod = PyDBML(p_mod.dbml)
            note2 = p_mod.tables[0].note
            self.assertEqual(source_text, note2.text)
