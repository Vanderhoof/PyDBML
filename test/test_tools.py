from unittest import TestCase

from pydbml.classes import Note
from pydbml.tools import comment_to_dbml
from pydbml.tools import comment_to_sql
from pydbml.tools import indent
from pydbml.tools import note_option_to_dbml


class TestCommentToDBML(TestCase):
    def test_comment(self) -> None:
        oneline = 'comment'
        self.assertEqual(f'// {oneline}\n', comment_to_dbml(oneline))

        expected = \
'''// 
// line1
// line2
// line3
// 
'''
        source = '\nline1\nline2\nline3\n'
        self.assertEqual(comment_to_dbml(source), expected)


class TestCommentToSQL(TestCase):
    def test_comment(self) -> None:
        oneline = 'comment'
        self.assertEqual(f'-- {oneline}\n', comment_to_sql(oneline))

        expected = \
'''-- 
-- line1
-- line2
-- line3
-- 
'''
        source = '\nline1\nline2\nline3\n'
        self.assertEqual(comment_to_sql(source), expected)


class TestNoteOptionToDBML(TestCase):
    def test_oneline(self) -> None:
        note = Note('one line note')
        self.assertEqual(f"note: 'one line note'", note_option_to_dbml(note))

    def test_multiline(self) -> None:
        note = Note('line1\nline2\nline3')
        expected = "note: '''line1\nline2\nline3'''"
        self.assertEqual(expected, note_option_to_dbml(note))


class TestIndent(TestCase):
    def test_empty(self) -> None:
        self.assertEqual(indent(''), '')

    def test_nonempty(self) -> None:
        oneline = 'one line text'
        self.assertEqual(indent(oneline), f'    {oneline}')
        source = 'line1\nline2\nline3'
        expected = '    line1\n    line2\n    line3'
        self.assertEqual(indent(source), expected)
        expected2 = '  line1\n  line2\n  line3'
        self.assertEqual(indent(source, 2), expected2)
