from pydbml.classes import Note
from pydbml.renderer.dbml.default.utils import note_option_to_dbml, comment_to_dbml


class TestNoteOptionsToDBML:
    @staticmethod
    def test_oneline() -> None:
        note = Note("One line note")
        expected = "note: 'One line note'"
        assert note_option_to_dbml(note) == expected

    @staticmethod
    def test_multiline() -> None:
        note = Note("Multiline\nnote")
        expected = "note: '''Multiline\nnote'''"
        assert note_option_to_dbml(note) == expected


def test_comment_to_dbml() -> None:
    assert comment_to_dbml("Simple comment") == "// Simple comment\n"
