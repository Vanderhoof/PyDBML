from pydbml.classes import Column
from pydbml.renderer.sql.default import render_column


class TestRenderColumn:
    @staticmethod
    def test_simple(simple_column: Column) -> None:
        expected = '"id" integer'

        assert render_column(simple_column), expected

    @staticmethod
    def test_complex(complex_column: Column) -> None:
        expected = (
            "-- This is a counter column\n"
            '"counter" "product status" PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL DEFAULT '
            "0"
        )
        assert render_column(complex_column) == expected

    @staticmethod
    def test_string(string_column: Column) -> None:
        expected = (
            "-- This is a defaulted string column\n"
            '"name" varchar(255) UNIQUE NOT NULL DEFAULT '
            "'value''s'"
        )
        assert render_column(string_column) == expected

    @staticmethod
    def test_string(boolean_column: Column) -> None:
        expected = (
            "-- This is a defaulted boolean column\n"
            '"enabled" boolean NOT NULL DEFAULT '
            "False"
        )
        assert render_column(boolean_column) == expected
