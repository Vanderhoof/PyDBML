from unittest import TestCase

from pydbml.classes import Note
from pydbml.tools import comment_to_dbml, remove_indentation
from pydbml.tools import comment_to_sql
from pydbml.tools import indent
from pydbml.tools import note_option_to_dbml
from pydbml.tools import strip_empty_lines


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

    def test_oneline_with_quote(self) -> None:
        note = Note('one line\'d note')
        self.assertEqual(f"note: 'one line\\'d note'", note_option_to_dbml(note))

    def test_multiline(self) -> None:
        note = Note('line1\nline2\nline3')
        expected = "note: '''line1\nline2\nline3'''"
        self.assertEqual(expected, note_option_to_dbml(note))

    def test_multiline_with_quotes(self) -> None:
        note = Note('line1\n\'\'\'line2\nline3')
        expected = "note: '''line1\n\\'''line2\nline3'''"
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


class TestStripEmptyLines(TestCase):
    def test_empty(self) -> None:
        source = ''
        self.assertEqual(strip_empty_lines(source), source)

    def test_no_empty_lines(self) -> None:
        source = 'line1\n\n\nline2'
        self.assertEqual(strip_empty_lines(source), source)

    def test_empty_lines(self) -> None:
        stripped = '   line1\n\n line2'
        source = f'\n \n   \n\t \t \n  \n{stripped}\n\n\n   \n \t \n\t \n   \n'
        self.assertEqual(strip_empty_lines(source), stripped)

    def test_one_empty_line(self) -> None:
        stripped = '   line1\n\n line2'
        source = f'\n{stripped}'
        self.assertEqual(strip_empty_lines(source), stripped)
        source = f'{stripped}\n'
        self.assertEqual(strip_empty_lines(source), stripped)

    def test_end(self) -> None:
        stripped = '   line1\n\n line2'
        source = f'\n{stripped}\n   '
        self.assertEqual(strip_empty_lines(source), stripped)


class TestRemoveIndentation(TestCase):
    def test_empty(self) -> None:
        source = ''
        self.assertEqual(remove_indentation(source), source)

    def test_not_empty(self) -> None:
        source = '    line1\n     line2'
        expected = 'line1\n line2'
        self.assertEqual(remove_indentation(source), expected)
