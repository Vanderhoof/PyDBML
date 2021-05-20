"""
These integration tests are based on examples in official DBML docs: https://www.dbml.org/docs/

They should kept up to date to ensure all features are supported by PyDBML.
"""
import os

from pathlib import Path
from unittest import TestCase

from pydbml import PyDBML
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import TableNotFoundError


TEST_DOCS_PATH = Path(os.path.abspath(__file__)).parent / 'test_data/docs'


class TestDocs(TestCase):
    def test_example(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'example.dbml')
        users, posts = results.tables
        self.assertEqual([c.name for c in users.columns], ['id', 'username', 'role', 'created_at'])
        self.assertEqual([c.name for c in posts.columns], ['id', 'title', 'body', 'user_id', 'created_at'])

        self.assertEqual(len(results.refs), 1)
        ref = results.refs[0]
        self.assertEqual((posts, users), (ref.table1, ref.table2))

    def test_project(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'project.dbml')
        proj = results.project
        self.assertEqual(proj.name, 'project_name')
        self.assertEqual(proj.items, {'database_type': 'PostgreSQL'})
        self.assertEqual(proj.note.text, 'Description of the project')

    def test_table_definition(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'table_definition.dbml')
        self.assertEqual(len(results.tables), 1)
        self.assertEqual(results.tables[0].name, 'table_name')

        table = results.tables[0]
        self.assertEqual([c.name for c in table.columns], ['column_name', 'example', 'json_column', 'jsonb_column', 'decimal_column'])

    def test_table_alias(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'table_alias.dbml')
        u, posts = results.tables
        self.assertEqual(u.alias, 'U')
        self.assertIsNone(posts.alias)
        self.assertEqual([c.name for c in u.columns], ['id'])
        self.assertEqual([c.name for c in posts.columns], ['id', 'user_id'])

        self.assertEqual(len(results.refs), 1)
        ref = results.refs[0]
        self.assertEqual((u, posts), (ref.table1, ref.table2))

    def test_table_notes(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'table_notes.dbml')
        self.assertEqual(len(results.tables), 1)
        self.assertEqual(results.tables[0].name, 'users')

        table = results.tables[0]
        self.assertEqual([c.name for c in table.columns], ['id', 'status'])
        self.assertEqual(table.note.text, 'Stores user data')
        self.assertEqual(table['status'].note.text, 'status')

    def test_column_settings(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'column_settings.dbml')
        self.assertEqual(len(results.tables), 1)
        self.assertEqual(results.tables[0].name, 'buildings')

        table = results.tables[0]
        self.assertEqual([c.name for c in table.columns], ['address', 'id', 'nullable', 'counter'])
        address, id_, nullable, counter = table.columns
        self.assertTrue(address.unique)
        self.assertTrue(address.not_null)
        self.assertEqual(address.note.text, 'to include unit number')

        self.assertTrue(id_.pk)
        self.assertTrue(id_.unique)
        self.assertEqual(id_.note.text, 'Number')
        self.assertEqual(id_.default, 123)

        self.assertFalse(nullable.not_null)

        self.assertTrue(counter.autoinc)

    def test_default_value(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'default_value.dbml')
        self.assertEqual(len(results.tables), 1)
        self.assertEqual(results.tables[0].name, 'users')

        table = results.tables[0]
        self.assertEqual([c.name for c in table.columns], ['id', 'username', 'full_name', 'gender', 'created_at', 'rating'])
        *_, gender, created_at, rating = table.columns
        self.assertEqual(gender.default, 'm')
        self.assertEqual(created_at.default, '(now())')
        self.assertEqual(rating.default, 10)

    def test_index_definition(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'index_definition.dbml')
        self.assertEqual(len(results.tables), 1)
        self.assertEqual(results.tables[0].name, 'bookings')

        table = results.tables[0]
        self.assertEqual([c.name for c in table.columns], ['id', 'country', 'booking_date', 'created_at'])
        self.assertEqual(len(table.indexes), 8)

        ix = table.indexes
        self.assertEqual(ix[0].subjects, [table['id'], table['country']])
        self.assertEqual(ix[0].comment, 'composite primary key')
        self.assertTrue(ix[0].pk)

        self.assertEqual(ix[1].subjects, [table['created_at']])
        self.assertEqual(ix[1].name, 'created_at_index')
        self.assertEqual(ix[1].note.text, 'Date')

        self.assertEqual(ix[2].subjects, [table['booking_date']])

        self.assertEqual(ix[3].subjects, [table['country'], table['booking_date']])
        self.assertTrue(ix[3].unique)

        self.assertEqual(ix[4].subjects, [table['booking_date']])
        self.assertEqual(ix[4].type, 'hash')

        self.assertEqual(ix[5].subjects, ['(id*2)'])

        self.assertEqual(ix[6].subjects, ['(id*3)', '(getdate())'])

        self.assertEqual(ix[7].subjects, ['(id*3)', table['id']])

    def test_relationships(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'relationships_1.dbml')
        posts, reviews, users = results.tables

        rf = results.refs

        self.assertEqual(rf[0].table1, posts)
        self.assertEqual(rf[0].table2, users)
        self.assertEqual(rf[0].type, '>')

        self.assertEqual(rf[1].table1, reviews)
        self.assertEqual(rf[1].table2, users)
        self.assertEqual(rf[1].type, '>')

        results = PyDBML.parse_file(TEST_DOCS_PATH / 'relationships_2.dbml')
        posts, reviews, users = results.tables

        rf = results.refs

        self.assertEqual(rf[0].table1, users)
        self.assertEqual(rf[0].table2, posts)
        self.assertEqual(rf[0].type, '<')

        self.assertEqual(rf[1].table1, users)
        self.assertEqual(rf[1].table2, reviews)
        self.assertEqual(rf[1].type, '<')

    def test_relationships_composite(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'relationships_composite.dbml')
        merchant_periods, merchants = results.tables

        rf = results.refs

        self.assertEqual(len(rf), 1)

        self.assertEqual(rf[0].table1, merchant_periods)
        self.assertEqual(rf[0].table2, merchants)
        self.assertEqual(rf[0].type, '>')
        self.assertEqual(
            rf[0].col1,
            [
                merchant_periods['merchant_id'],
                merchant_periods['country_code'],
            ]
        )
        self.assertEqual(
            rf[0].col2,
            [
                merchants['id'],
                merchants['country_code'],
            ]
        )

    def test_relationship_settings(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'relationship_settings.dbml')
        merchant_periods, merchants = results.tables

        rf = results.refs

        self.assertEqual(len(rf), 1)

        self.assertEqual(rf[0].table1, merchant_periods)
        self.assertEqual(rf[0].table2, merchants)
        self.assertEqual(rf[0].type, '>')
        self.assertEqual(rf[0].on_delete, 'cascade')
        self.assertEqual(rf[0].on_update, 'no action')

    def test_note_definition(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'note_definition.dbml')
        self.assertEqual(len(results.tables), 1)
        users = results['users']
        self.assertEqual(users.note.text, 'This is a note of this table')

    def test_project_notes(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'project_notes.dbml')
        project = results.project

        self.assertEqual(project.name, 'DBML')
        self.assertTrue(project.note.text.startswith('\n    # DBML - Database Markup Language\n    DBML'))

    def test_column_notes(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'column_notes.dbml')
        users = results['users']

        self.assertEqual(users.note.text, 'Stores user data')
        self.assertEqual(users['column_name'].note.text, 'replace text here')
        self.assertTrue('shipped' in users['status'].note.text)

    def test_enum_definition(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'enum_definition.dbml')
        jobs = results['jobs']
        jobs['status'].type == 'job_status'

        self.assertEqual(len(results.enums), 1)
        js = results.enums[0]

        self.assertEqual(js.name, 'job_status')
        self.assertEqual([ei.name for ei in js.items], ['created', 'running', 'done', 'failure'])

    def test_table_group(self) -> None:
        results = PyDBML.parse_file(TEST_DOCS_PATH / 'table_group.dbml')

        self.assertEqual(len(results.tables), 5)
        self.assertEqual(len(results.table_groups), 2)

        tb1, tb2, tb3, merchants, countries = results.tables

        tg1, tg2 = results.table_groups

        self.assertEqual(tg1.name, 'tablegroup_name')
        self.assertEqual(tg1.items, [tb1, tb2, tb3])
        self.assertEqual(tg2.name, 'e_commerce1')
        self.assertEqual(tg2.items, [merchants, countries])
