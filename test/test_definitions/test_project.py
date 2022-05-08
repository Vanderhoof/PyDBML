from unittest import TestCase

from pyparsing import ParseSyntaxException
from pyparsing import ParserElement

from pydbml.definitions.project import project
from pydbml.definitions.project import project_field


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestProjectField(TestCase):
    def test_ok(self) -> None:
        val = "field: 'value'"
        project_field.parseString(val, parseAll=True)

    def test_nok(self) -> None:
        val = "field: value"
        with self.assertRaises(ParseSyntaxException):
            project_field.parseString(val, parseAll=True)


class TestProject(TestCase):
    def test_empty(self) -> None:
        val = 'project name {}'
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')

    def test_fields(self) -> None:
        val = "project name {field1: 'value1' field2: 'value2'}"
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items['field1'], 'value1')
        self.assertEqual(res[0].items['field2'], 'value2')

    def test_fields_and_note(self) -> None:
        val = "project name {\nfield1: 'value1'\nfield2: 'value2'\nnote: 'note value'}"
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items['field1'], 'value1')
        self.assertEqual(res[0].items['field2'], 'value2')
        self.assertEqual(res[0].note.text, 'note value')

    def test_comment(self) -> None:
        val = "//comment before\nproject name {\nfield1: 'value1'\nfield2: 'value2'\nnote: 'note value'}"
        res = project.parseString(val, parseAll=True)
        self.assertEqual(res[0].name, 'name')
        self.assertEqual(res[0].items['field1'], 'value1')
        self.assertEqual(res[0].items['field2'], 'value2')
        self.assertEqual(res[0].note.text, 'note value')
        self.assertEqual(res[0].comment, 'comment before')
