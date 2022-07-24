from pydbml.classes import Project
from pydbml.classes import Note

from unittest import TestCase


class TestProject(TestCase):
    def test_dbml_note(self):
        p = Project('myproject', note='Project note')
        expected = \
'''Project "myproject" {
    Note {
        'Project note'
    }
}'''
        self.assertEqual(p.dbml, expected)

    def test_dbml_full(self):
        p = Project(
            'myproject',
            items={
                'database_type': 'PostgreSQL',
                'story': "One day I was eating my cantaloupe and\nI thought, why shouldn't I?\nWhy shouldn't I create a database?"
            },
            comment='Multiline\nProject comment',
            note='Multiline\nProject note')
        expected = \
"""// Multiline
// Project comment
Project "myproject" {
    database_type: 'PostgreSQL'
    story: '''One day I was eating my cantaloupe and
    I thought, why shouldn't I?
    Why shouldn't I create a database?'''
    Note {
        '''
        Multiline
        Project note
        '''
    }
}"""
        self.assertEqual(p.dbml, expected)

    def test_dbml_space(self) -> None:
        p = Project('My project', {'a': 'b'})
        expected = \
'''Project "My project" {
    a: 'b'
}'''
        self.assertEqual(p.dbml, expected)

    def test_note_property(self):
        note1 = Note('column note')
        p = Project('myproject')
        p.note = note1
        self.assertIs(p.note.parent, p)
