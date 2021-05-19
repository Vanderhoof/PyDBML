from unittest import TestCase

from pyparsing import ParseException
from pyparsing import ParseSyntaxException
from pyparsing import ParserElement

from pydbml.definitions.index import composite_index_syntax
from pydbml.definitions.index import index
from pydbml.definitions.index import index_setting
from pydbml.definitions.index import index_settings
from pydbml.definitions.index import index_type
from pydbml.definitions.index import indexes
from pydbml.definitions.index import single_index_syntax
from pydbml.definitions.index import subject


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestIndexType(TestCase):
    def test_correct(self) -> None:
        val = 'Type: BTREE'
        res = index_type.parseString(val, parseAll=True)
        self.assertEqual(res['type'], 'btree')
        val2 = 'type:\nhash'
        res2 = index_type.parseString(val2, parseAll=True)
        self.assertEqual(res2['type'], 'hash')

    def test_incorrect(self) -> None:
        val = 'type: wrong'
        with self.assertRaises(ParseSyntaxException):
            index_type.parseString(val, parseAll=True)


class TestIndexSetting(TestCase):
    def test_unique(self) -> None:
        val = 'unique'
        res = index_setting.parseString(val, parseAll=True)
        self.assertEqual(res['unique'], 'unique')

    def test_type(self) -> None:
        val = 'type: btree'
        res = index_setting.parseString(val, parseAll=True)
        self.assertEqual(res['type'], 'btree')

    def test_name(self) -> None:
        val = 'name: "index name"'
        res = index_setting.parseString(val, parseAll=True)
        self.assertEqual(res['name'], 'index name')

    def test_wrong_name(self) -> None:
        val = 'name: index name'
        with self.assertRaises(ParseSyntaxException):
            index_setting.parseString(val, parseAll=True)
        val2 = 'name:,'
        with self.assertRaises(ParseSyntaxException):
            index_setting.parseString(val2, parseAll=True)

    def test_note(self) -> None:
        val = 'note: "note text"'
        res = index_setting.parseString(val, parseAll=True)
        self.assertEqual(res['note'].text, 'note text')


class TestIndexSettings(TestCase):
    def test_unique(self) -> None:
        val = '[unique]'
        res = index_settings.parseString(val, parseAll=True)
        self.assertTrue(res[0]['unique'])

    def test_name_type_multiline(self) -> None:
        val = '[\nname: "index name"\n,\ntype:\nbtree\n]'
        res = index_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['type_'], 'btree')
        self.assertEqual(res[0]['name'], 'index name')

    def test_pk(self) -> None:
        val = '[\npk\n]'
        res = index_settings.parseString(val, parseAll=True)
        self.assertTrue(res[0]['pk'])

    def test_wrong_pk(self) -> None:
        val = '[pk, name: "not allowed"]'
        with self.assertRaises(ParseSyntaxException):
            index_settings.parseString(val, parseAll=True)
        val2 = '[note: "pk not allowed", pk]'
        with self.assertRaises(ParseSyntaxException):
            index_settings.parseString(val2, parseAll=True)

    def test_all(self) -> None:
        val = '[type: hash, name: "index name", note: "index note", unique]'
        res = index_settings.parseString(val, parseAll=True)
        self.assertEqual(res[0]['type_'], 'hash')
        self.assertEqual(res[0]['name'], 'index name')
        self.assertEqual(res[0]['note'].text, 'index note')
        self.assertTrue(res[0]['unique'])


class TestSubject(TestCase):
    def test_name(self) -> None:
        val = 'my_column'
        res = subject.parseString(val, parseAll=True)
        self.assertEqual(res[0], val)

    def test_expression(self) -> None:
        val = '`id*3`'
        res = subject.parseString(val, parseAll=True)
        self.assertEqual(res[0], '(id*3)')

    def test_wrong(self) -> None:
        val = '12d*('
        with self.assertRaises(ParseException):
            subject.parseString(val, parseAll=True)


class TestSingleIndex(TestCase):
    def test_no_settings(self) -> None:
        val = 'my_column'
        res = single_index_syntax.parseString(val, parseAll=True)
        self.assertEqual(res['subject'], val)

    def test_settings(self) -> None:
        val = 'my_column [unique]'
        res = single_index_syntax.parseString(val, parseAll=True)
        self.assertEqual(res['subject'], 'my_column')
        self.assertTrue(res['settings']['unique'])

    def test_settings_on_new_line(self) -> None:
        val = 'my_column\n[unique]'
        with self.assertRaises(ParseException):
            single_index_syntax.parseString(val, parseAll=True)


class TestCompositeIndex(TestCase):
    def test_no_settings(self) -> None:
        val = '(my_column, my_another_column)'
        res = composite_index_syntax.parseString(val, parseAll=True)
        self.assertIn('my_column', list(res['subject']))
        self.assertIn('my_another_column', list(res['subject']))
        self.assertEqual(len(res['subject']), 2)

    def test_settings(self) -> None:
        val = '(my_column, my_another_column) [unique]'
        res = composite_index_syntax.parseString(val, parseAll=True)
        self.assertIn('my_column', list(res['subject']))
        self.assertIn('my_another_column', list(res['subject']))
        self.assertEqual(len(res['subject']), 2)
        self.assertTrue(res['settings']['unique'])

    def test_new_line(self) -> None:
        val = '(my_column,\nmy_another_column) [unique]'
        with self.assertRaises(ParseException):
            composite_index_syntax.parseString(val, parseAll=True)
        val2 = '(my_column, my_another_column)\n[unique]'
        with self.assertRaises(ParseException):
            composite_index_syntax.parseString(val2, parseAll=True)


class TestIndex(TestCase):
    def test_single(self) -> None:
        val = 'my_column'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column'])

    def test_expression(self) -> None:
        val = '(`id*3`)'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['(id*3)'])

    def test_composite(self) -> None:
        val = '(my_column, my_another_column)'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column', 'my_another_column'])

    def test_composite_with_expression(self) -> None:
        val = '(`id*3`, fieldname)'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['(id*3)', 'fieldname'])

    def test_with_settings(self) -> None:
        val = '(my_column, my_another_column) [unique]'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column', 'my_another_column'])
        self.assertTrue(res[0].unique)

    def test_comment_above(self) -> None:
        val = '//comment above\nmy_column [unique]'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column'])
        self.assertTrue(res[0].unique)
        self.assertEqual(res[0].comment, 'comment above')

    def test_comment_after(self) -> None:
        val = 'my_column [unique] //comment after'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column'])
        self.assertTrue(res[0].unique)
        self.assertEqual(res[0].comment, 'comment after')
        val = 'my_column //comment after'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column'])
        self.assertEqual(res[0].comment, 'comment after')

    def test_both_comments(self) -> None:
        val = '//comment before\nmy_column [unique] //comment after'
        res = index.parseString(val, parseAll=True)
        self.assertEqual(res[0].subject_names, ['my_column'])
        self.assertTrue(res[0].unique)
        self.assertEqual(res[0].comment, 'comment after')


class TestIndexes(TestCase):
    def test_valid(self) -> None:
        val = '''  indexes {
      (id, country) [pk] // composite primary key
      "created_at" booking_date (country, booking_date) [
        name: 'name'
        ,
        unique
      ]
      booking_date [type:
      btree]
      (`id*2`)
      (`id*3`,`getdate()`)
      (`id*3`,id)
  }'''
        res = indexes.parseString(val)
        self.assertEqual(len(res), 8)

    def test_invalid(self) -> None:
        val = 'indexes {my_column'
        with self.assertRaises(ParseSyntaxException):
            indexes.parseString(val)
