from enum import Enum
from typing import Any
from unittest.mock import Mock, patch

import pytest

from pydbml.classes import Column, Note
from pydbml.renderer.dbml.default.column import (
    default_to_str,
    render_options,
    render_column,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("test", "'test'"),
        (1, "1"),
        (1.0, "1.0"),
        (True, "True"),
        ("False", "false"),
        ("null", "null"),
    ],
)
def test_default_to_str(input: Any, expected: str) -> None:
    assert default_to_str(input) == expected


class TestRenderOptions:
    @staticmethod
    def test_refs(simple_column: Column) -> None:
        simple_column.get_refs = Mock(
            return_value=[
                Mock(dbml="ref1", inline=True),
                Mock(dbml="ref2", inline=False),
                Mock(dbml="ref3", inline=True),
            ]
        )
        assert render_options(simple_column) == " [ref1, ref3]"

    @staticmethod
    def test_pk(simple_column_with_table: Column) -> None:
        simple_column_with_table.pk = True
        assert render_options(simple_column_with_table) == " [pk]"

    @staticmethod
    def test_autoinc(simple_column_with_table: Column) -> None:
        simple_column_with_table.autoinc = True
        assert render_options(simple_column_with_table) == " [increment]"

    @staticmethod
    def test_default(simple_column_with_table: Column) -> None:
        simple_column_with_table.default = "6"
        assert render_options(simple_column_with_table) == " [default: '6']"

    @staticmethod
    def test_unique(simple_column_with_table: Column) -> None:
        simple_column_with_table.unique = True
        assert render_options(simple_column_with_table) == " [unique]"

    @staticmethod
    def test_not_null(simple_column_with_table: Column) -> None:
        simple_column_with_table.not_null = True
        assert render_options(simple_column_with_table) == " [not null]"

    @staticmethod
    def test_note(simple_column_with_table: Column) -> None:
        simple_column_with_table.note = Note("note")
        with patch(
            "pydbml.renderer.dbml.default.column.note_option_to_dbml",
            Mock(return_value="note"),
        ):
            assert render_options(simple_column_with_table) == " [note]"

    @staticmethod
    def test_no_options(simple_column_with_table: Column) -> None:
        assert render_options(simple_column_with_table) == ""

    @staticmethod
    def test_all_options(complex_column: Column) -> None:
        complex_column.get_refs = Mock(
            return_value=[
                Mock(dbml="ref1", inline=True),
                Mock(dbml="ref2", inline=False),
                Mock(dbml="ref3", inline=True),
            ]
        )
        complex_column.default = "null"
        with patch(
            "pydbml.renderer.dbml.default.column.note_option_to_dbml",
            Mock(return_value="note"),
        ):
            assert (
                render_options(complex_column)
                == " [ref1, ref3, pk, increment, default: null, unique, not null, note]"
            )


class TestRenderColumn:
    @staticmethod
    def test_comment(simple_column_with_table: Column) -> None:
        simple_column_with_table.comment = "Simple comment"
        expected = '// Simple comment\n"id" integer'
        assert render_column(simple_column_with_table) == expected

    @staticmethod
    def test_enum(simple_column_with_table: Column, enum1: Enum) -> None:
        simple_column_with_table.type = enum1
        expected = '"id" "product status"'
        assert render_column(simple_column_with_table) == expected

    @staticmethod
    def test_complex(complex_column_with_table: Column) -> None:
        expected = (
            "// This is a counter column\n"
            '"counter" "product status" [pk, increment, unique, not null, note: \'This is '
            "a note for the column']"
        )
        assert render_column(complex_column_with_table) == expected
