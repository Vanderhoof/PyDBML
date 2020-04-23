from pyparsing import ParseSyntaxException, ParserElement
from pydbml.definitions.project import (project_field, project)
from unittest import TestCase


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestProjectField(TestCase):
    def test_ok(self):
        val = "field: 'value'"
        project_field.parseString(val, parseAll=True)

    def test_nok(self):
        val = "field: value"
        with self.assertRaises(ParseSyntaxException):
            project_field.parseString(val, parseAll=True)


class TestProject(TestCase):
    def test_empty(self):
        val = 'project name {}'
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')

    def test_fields(self):
        val = "project name {field1: 'value1' field2: 'value2'}"
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items['field1'], 'value1')
        self.assertEqual(res[0].items['field2'], 'value2')

    def test_fields_and_note(self):
        val = "project name {\nfield1: 'value1'\nfield2: 'value2'\nnote: 'note value'}"
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items['field1'], 'value1')
        self.assertEqual(res[0].items['field2'], 'value2')
        self.assertEqual(res[0].note.text, 'note value')

    def test_comment(self):
        val = "//comment before\nproject name {\nfield1: 'value1'\nfield2: 'value2'\nnote: 'note value'}"
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items['field1'], 'value1')
        self.assertEqual(res[0].items['field2'], 'value2')
        self.assertEqual(res[0].note.text, 'note value')
        self.assertEqual(res[0].comment, 'comment before')
