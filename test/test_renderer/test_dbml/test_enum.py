from pydbml.classes import Enum, EnumItem, Note
from pydbml.renderer.dbml.default.enum import (
    get_full_name_for_dbml,
    render_enum_item,
    render_enum,
)


class TestGetFullNameForDBML:
    @staticmethod
    def test_no_schema(enum1: Enum) -> None:
        enum1.schema = ""
        assert get_full_name_for_dbml(enum1) == '"product status"'

    @staticmethod
    def test_with_schema(enum1: Enum) -> None:
        enum1.schema = "public"
        assert get_full_name_for_dbml(enum1) == '"public"."product status"'


class TestRenderEnumItem:
    @staticmethod
    def test_simple(enum_item1: EnumItem) -> None:
        assert render_enum_item(enum_item1) == '"en-US"'

    @staticmethod
    def test_comment(enum_item1: EnumItem) -> None:
        enum_item1.comment = "comment"
        expected = '// comment\n"en-US"'
        assert render_enum_item(enum_item1) == expected

    @staticmethod
    def test_note(enum_item1: EnumItem) -> None:
        enum_item1.note = Note("Enum item note")
        expected = "\"en-US\" [note: 'Enum item note']"
        assert render_enum_item(enum_item1) == expected


class TestEnum:
    @staticmethod
    def test_simple(enum1: Enum) -> None:
        expected = 'Enum "public"."product status" {\n    "production"\n    "development"\n}'
        assert render_enum(enum1) == expected

    @staticmethod
    def test_comment(enum1: Enum) -> None:
        enum1.comment = "comment"
        expected = '// comment\nEnum "public"."product status" {\n    "production"\n    "development"\n}'
        assert render_enum(enum1) == expected
