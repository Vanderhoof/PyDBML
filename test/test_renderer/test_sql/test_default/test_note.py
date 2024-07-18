from textwrap import dedent

from pydbml.classes import Note, Table, Index
from pydbml.renderer.sql.default.note import prepare_text_for_sql, generate_comment_on, render_note


def test_prepare_text_for_sql() -> None:
    text = dedent(
        """\
    First line break is preserved
    second line break \\
    is 'ignored' """
    )
    expected = 'First line break is preserved\nsecond line break is "ignored" '
    assert prepare_text_for_sql(Note(text)) == expected


def test_generate_comment_on(note1: Note) -> None:
    expected = "COMMENT ON TABLE \"table1\" IS 'Simple note';"

    assert generate_comment_on(note1, "Table", "table1") == expected


class TestRenderNote:
    @staticmethod
    def test_table_note_with_text(note1: Note, table1: Table) -> None:
        table1.note = note1
        expected = "COMMENT ON TABLE \"products\" IS 'Simple note';"
        assert render_note(note1) == expected

    @staticmethod
    def test_table_note_without_text(note1: Note, table1: Table) -> None:
        table1.note = note1
        note1.text = ""
        assert render_note(note1) == ""

    @staticmethod
    def test_index_note(index1: Index, multiline_note: Note) -> None:
        index1.note = multiline_note
        expected = dedent(
            """\
            -- This is a multiline note.
            -- It has multiple lines."""
        )
        assert render_note(multiline_note) == expected
