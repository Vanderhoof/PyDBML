from unittest import TestCase

from pydbml.classes import Note
from pydbml.parser.blueprints import NoteBlueprint


class TestNote(TestCase):
    def test_build(self) -> None:
        bp = NoteBlueprint(text='Note text')
        result = bp.build()
        self.assertIsInstance(result, Note)
        self.assertEqual(result.text, bp.text)

    def test_preformat_not_needed(self):
        oneline = 'One line of note text'
        multiline = 'Multiline\nnote\n\ntext'
        long_line = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Aspernatur quidem adipisci, impedit, ut illum dolorum consequatur odio voluptate numquam ea itaque excepturi, a libero placeat corrupti. Amet beatae suscipit necessitatibus. Ea expedita explicabo iste quae rem aliquam minus cumque eveniet enim delectus, alias aut impedit quaerat quia ex, aliquid sint amet iusto rerum! Sunt deserunt ea saepe corrupti officiis. Assumenda.'

        bp = NoteBlueprint(text=oneline)
        self.assertEqual(bp._preformat_text(), oneline)
        bp = NoteBlueprint(text=multiline)
        self.assertEqual(bp._preformat_text(), multiline)
        bp = NoteBlueprint(text=long_line)
        self.assertEqual(bp._preformat_text(), long_line)

    def test_preformat_needed(self):
        uniform_indentation = '    line1\n    line2\n    line3'
        varied_indentation = '   line1\n     line2\n\n    line3'
        empty_lines = '\n\n\n\n\n\n\nline1\nline2\nline3\n\n\n\n\n\n\n'
        empty_indented_lines = '\n  \n\n   \n\n    line1\n    line2\n    line3\n\n\n\n  \n\n\n'

        exptected = 'line1\nline2\nline3'
        bp = NoteBlueprint(text=uniform_indentation)
        self.assertEqual(bp._preformat_text(), exptected)

        exptected = 'line1\n  line2\n\n line3'
        bp = NoteBlueprint(text=varied_indentation)
        self.assertEqual(bp._preformat_text(), exptected)

        exptected = 'line1\nline2\nline3'
        bp = NoteBlueprint(text=empty_lines)
        self.assertEqual(bp._preformat_text(), exptected)

        exptected = 'line1\nline2\nline3'
        bp = NoteBlueprint(text=empty_indented_lines)
        self.assertEqual(bp._preformat_text(), exptected)
