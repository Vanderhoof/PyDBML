from pydbml._classes.sticky_note import StickyNote
from pydbml.renderer.dbml.default import render_sticky_note


class TestRenderNote:
    @staticmethod
    def test_oneline() -> None:
        note = StickyNote(name='mynote', text="Note text")
        assert render_sticky_note(note) == "Note mynote {\n    'Note text'\n}"

    @staticmethod
    def test_multiline() -> None:
        note = StickyNote(name='mynote', text="Note text\nwith multiple lines")
        assert (
            render_sticky_note(note)
            == "Note mynote {\n    '''\n    Note text\n    with multiple lines'''\n}"
        )
