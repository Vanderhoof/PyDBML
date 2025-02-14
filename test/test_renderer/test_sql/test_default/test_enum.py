from pydbml.classes import EnumItem, Enum
from pydbml.renderer.sql.default import render_enum, render_enum_item


class TestRenderEnumItem:
    @staticmethod
    def test_simple(enum_item1: EnumItem):
        expected = "'en-US',"
        assert render_enum_item(enum_item1) == expected

    @staticmethod
    def test_comment(enum_item1: EnumItem):
        enum_item1.comment = "Test comment"
        expected = "-- Test comment\n'en-US',"
        assert render_enum_item(enum_item1) == expected


class TestRenderEnum:
    @staticmethod
    def test_simple_enum(enum1: Enum) -> None:
        expected = (
            'CREATE TYPE "product status" AS ENUM (\n'
            "  'production',\n"
            "  'development'\n"
            ");"
        )
        assert render_enum(enum1) == expected

    @staticmethod
    def test_comments(enum1: Enum) -> None:
        enum1.comment = "Enum comment"
        expected = (
            "-- Enum comment\n"
            'CREATE TYPE "product status" AS ENUM (\n'
            "  'production',\n"
            "  'development'\n"
            ");"
        )
        assert render_enum(enum1) == expected
