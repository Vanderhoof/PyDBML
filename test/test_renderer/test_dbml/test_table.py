from pydbml import Database
from pydbml.classes import Table, Index, Note
from pydbml.renderer.dbml.default.table import (
    get_full_name_for_dbml,
    render_header,
    render_indexes,
    render_table,
)


class TestGetFullNameForDBML:
    @staticmethod
    def test_no_schema(table1: Table) -> None:
        table1.schema = "public"
        assert get_full_name_for_dbml(table1) == '"products"'

    @staticmethod
    def test_with_schema(table1: Table) -> None:
        table1.schema = "myschema"
        assert get_full_name_for_dbml(table1) == '"myschema"."products"'


class TestRenderHeader:
    @staticmethod
    def test_simple(table1: Table) -> None:
        expected = 'Table "products" '
        assert render_header(table1) == expected

    @staticmethod
    def test_alias(table1: Table) -> None:
        table1.alias = "p"
        expected = 'Table "products" as "p" '
        assert render_header(table1) == expected

    @staticmethod
    def test_header_color(table1: Table) -> None:
        table1.header_color = "red"
        expected = 'Table "products" [headercolor: red] '
        assert render_header(table1) == expected

    @staticmethod
    def test_all(table1: Table) -> None:
        table1.alias = "p"
        table1.header_color = "red"
        expected = 'Table "products" as "p" [headercolor: red] '
        assert render_header(table1) == expected


class TestRenderIndexes:
    @staticmethod
    def test_no_indexes(table1: Table) -> None:
        assert render_indexes(table1) == ""

    @staticmethod
    def test_one_index(index1: Index) -> None:
        assert render_indexes(index1.table) == "\n    indexes {\n        name\n    }\n"


class TestRenderTable:
    @staticmethod
    def test_simple(db: Database, table1: Table) -> None:
        db.add(table1)
        expected = 'Table "products" {\n    "id" integer\n    "name" varchar\n}'
        assert render_table(table1) == expected

    @staticmethod
    def test_note_and_comment(db: Database, table1: Table) -> None:
        table1.comment = "Table comment"
        table1.note = Note("Table note")
        db.add(table1)
        expected = (
            "// Table comment\n"
            'Table "products" {\n'
            '    "id" integer\n'
            '    "name" varchar\n'
            "    Note {\n"
            "        'Table note'\n"
            "    }\n"
            "}"
        )
        assert render_table(table1) == expected

    @staticmethod
    def test_properties(db: Database, table1: Table) -> None:
        table1.properties = {"key": "value"}
        db.add(table1)
        db.allow_properties = True
        expected = (
            'Table "products" {\n'
            '    "id" integer\n'
            '    "name" varchar\n'
            "\n"
            "    key: 'value'\n"
            "}"
        )
        assert render_table(table1) == expected

    @staticmethod
    def test_properties_not_allowed(db: Database, table1: Table) -> None:
        table1.properties = {"key": "value"}
        db.add(table1)
        db.allow_properties = False
        expected = (
            'Table "products" {\n'
            '    "id" integer\n'
            '    "name" varchar\n'
            "}"
        )
        assert render_table(table1) == expected
