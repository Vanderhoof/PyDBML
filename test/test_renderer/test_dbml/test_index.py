from unittest.mock import patch, Mock

from pydbml.classes import Index, Expression, Note
from pydbml.renderer.dbml.default.index import render_subjects, render_options, render_index


class TestRenderSubjects:
    @staticmethod
    def test_column(index1: Index) -> None:
        assert render_subjects(index1.subjects) == "name"

    @staticmethod
    def test_expression(index1: Index) -> None:
        index1.subjects = [Expression("SUM(amount)")]
        assert render_subjects(index1.subjects) == "`SUM(amount)`"

    @staticmethod
    def test_string(index1: Index) -> None:
        index1.subjects = ["name"]
        assert render_subjects(index1.subjects) == "name"

    @staticmethod
    def test_multiple(index1: Index) -> None:
        index1.subjects.append(Expression("SUM(amount)"))
        index1.subjects.append("name")
        assert render_subjects(index1.subjects) == "(name, `SUM(amount)`, name)"


class TestRenderOptions:
    @staticmethod
    def test_name(index1: Index) -> None:
        index1.name = "index_name"
        assert render_options(index1) == " [name: 'index_name']"

    @staticmethod
    def test_pk(index1: Index) -> None:
        index1.pk = True
        assert render_options(index1) == " [pk]"

    @staticmethod
    def test_unique(index1: Index) -> None:
        index1.unique = True
        assert render_options(index1) == " [unique]"

    @staticmethod
    def test_type(index1: Index) -> None:
        index1.type = "hash"
        assert render_options(index1) == " [type: hash]"

    @staticmethod
    def test_note(index1: Index) -> None:
        index1.note = Note("note")
        with patch(
            "pydbml.renderer.dbml.default.index.note_option_to_dbml",
            Mock(return_value="note"),
        ):
            assert render_options(index1) == " [note]"

    @staticmethod
    def test_no_options(index1: Index) -> None:
        assert render_options(index1) == ""

    @staticmethod
    def test_all_options(index1: Index) -> None:
        index1.name = "index_name"
        index1.pk = True
        index1.unique = True
        index1.type = "hash"
        index1.note = Note("note")
        with patch(
            "pydbml.renderer.dbml.default.index.note_option_to_dbml",
            Mock(return_value="note"),
        ):
            assert (
                render_options(index1)
                == " [name: 'index_name', pk, unique, type: hash, note]"
            )


def test_render_index(index1: Index) -> None:
    index1.comment = "Index comment"
    with patch(
        "pydbml.renderer.dbml.default.index.render_subjects",
        Mock(return_value="subjects "),
    ) as render_subjects_mock:
        with patch(
            "pydbml.renderer.dbml.default.index.render_options",
            Mock(return_value="options"),
        ) as render_options_mock:
            assert render_index(index1) == '// Index comment\nsubjects options'
            assert render_subjects_mock.called
            assert render_options_mock.called
