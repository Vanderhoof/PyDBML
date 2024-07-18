from pydbml.classes import Note
from pydbml.renderer.dbml.default.note import render_note
from pydbml.renderer.dbml.default.utils import prepare_text_for_dbml


def test_prepare_text_for_dbml() -> None:
    note = Note("""Three quotes: ''', one quote: '.""")
    assert prepare_text_for_dbml(note) == "Three quotes: \\''', one quote: \\'."


class TestRenderNote:
    @staticmethod
    def test_oneline() -> None:
        note = Note("Note text")
        assert render_note(note) == "Note {\n    'Note text'\n}"

    @staticmethod
    def test_multiline() -> None:
        note = Note("Note text\nwith multiple lines")
        assert (
            render_note(note)
            == "Note {\n    '''\n    Note text\n    with multiple lines\n    '''\n}"
        )
