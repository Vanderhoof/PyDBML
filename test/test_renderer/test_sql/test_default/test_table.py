from typing import Tuple
from unittest.mock import Mock, patch

import pytest

import pydbml.renderer.sql.default.table
from pydbml import Database
from pydbml.classes import Table, Column, Reference, Note
from pydbml.renderer.sql.default.table import (
    get_references_for_sql,
    get_inline_references_for_sql,
    create_components,
    render_column_notes,
    create_body,
)


@pytest.fixture
def db1():
    return Database()


@pytest.fixture
def table1(db1: Database) -> Table:
    t = Table(
        name="products",
        columns=[
            Column("id", "integer", pk=True),
            Column("name", "varchar"),
        ],
    )
    db1.add(t)
    return t


@pytest.fixture
def table2(db1: Database) -> Table:
    t = Table(
        name="names",
        columns=[
            Column("id", "integer"),
            Column("name_val", "varchar"),
        ],
    )
    db1.add(t)
    return t


@pytest.fixture
def not_inline_refs(
    db1: Database, table1: Table, table2: Table
) -> Tuple[Reference, Reference, Reference]:
    r1 = Reference(">", table1[1], table2[1], inline=False)
    r2 = Reference("-", table1[0], table2[0], inline=False)
    r3 = Reference("<", table1[0], table2[1], inline=False)
    db1.add(r1)
    db1.add(r2)
    db1.add(r3)
    return r1, r2, r3


@pytest.fixture
def inline_refs(
    db1: Database, table1: Table, table2: Table
) -> Tuple[Reference, Reference, Reference]:
    r1 = Reference(">", table1[1], table2[1], inline=True)
    r2 = Reference("-", table1[0], table2[0], inline=True)
    r3 = Reference("<", table1[0], table2[1], inline=True)
    db1.add(r1)
    db1.add(r2)
    db1.add(r3)
    return r1, r2, r3


class TestGetReferencesForSQL:
    @staticmethod
    def test_get_references_for_sql_not_inline(
        table1: Table, table2: Table, not_inline_refs
    ) -> None:
        r1, r2, r3 = not_inline_refs
        assert get_references_for_sql(table1) == [r1, r2]
        assert get_references_for_sql(table2) == [r3]

    @staticmethod
    def test_get_references_for_sql_inline(
        table1: Table, table2: Table, inline_refs
    ) -> None:
        r1, r2, r3 = inline_refs
        assert get_references_for_sql(table1) == [r1, r2]
        assert get_references_for_sql(table2) == [r3]


class TestGetInlineReferencesForSQL:
    @staticmethod
    def test_inline(table1: Table, table2: Table, inline_refs) -> None:
        r1, r2, r3 = inline_refs
        assert get_inline_references_for_sql(table1) == [r1, r2]
        assert get_inline_references_for_sql(table2) == [r3]

    @staticmethod
    def test_not_inline(table1: Table, table2: Table, not_inline_refs) -> None:
        assert get_inline_references_for_sql(table1) == []
        assert get_inline_references_for_sql(table2) == []

    @staticmethod
    def test_abstract(table1: Table, table2: Table, inline_refs) -> None:
        table1.abstract = table2.abstract = True
        assert get_inline_references_for_sql(table1) == []
        assert get_inline_references_for_sql(table2) == []


class TestCreateBody:
    @staticmethod
    def test_create_body() -> None:
        table = Mock(
            columns=[Mock(), Mock()],
            indexes=[Mock(pk=True), Mock(pk=False)],
        )
        with patch(
            "pydbml.renderer.sql.default.table.get_inline_references_for_sql",
            Mock(return_value=[Mock()]),
        ) as get_inline_mock:
            with patch(
                "pydbml.renderer.sql.default.renderer.DefaultSQLRenderer.render",
                Mock(return_value=""),
            ) as render_mock:
                create_body(table)
                assert get_inline_mock.called
                assert render_mock.call_count == 4

    @staticmethod
    def test_composite_pk(table1: Table) -> None:
        table1.add_column(Column("id2", "integer", pk=True))
        expected = (
            '  "id" integer,\n'
            '  "name" varchar,\n'
            '  "id2" integer,\n'
            '  PRIMARY KEY ("id", "id2")'
        )
        assert create_body(table1) == expected


class TestCreateComponents:
    @staticmethod
    def test_simple(table1: Table) -> None:
        with patch(
            "pydbml.renderer.sql.default.table.create_body", Mock(return_value="body")
        ) as create_body_mock:
            expected = 'CREATE TABLE "products" (\nbody\n);'
            assert create_components(table1) == expected

    @staticmethod
    def test_comment(table1: Table) -> None:
        table1.comment = "Simple comment"
        with patch(
            "pydbml.renderer.sql.default.table.create_body", Mock(return_value="body")
        ) as create_body_mock:
            expected = '-- Simple comment\n\nCREATE TABLE "products" (\nbody\n);'
            assert create_components(table1) == expected

    @staticmethod
    def test_indexes(table1: Table) -> None:
        table1.indexes = [Mock(pk=False), Mock(pk=True)]
        with patch(
            "pydbml.renderer.sql.default.table.create_body", Mock(return_value="body")
        ) as create_body_mock:
            with patch(
                "pydbml.renderer.sql.default.renderer.DefaultSQLRenderer.render",
                Mock(return_value="index"),
            ) as render_mock:
                expected = 'CREATE TABLE "products" (\nbody\n);\n\nindex'
                assert create_components(table1) == expected


class TestRenderColumnNotes:
    @staticmethod
    def test_notes(table1: Table) -> None:
        table1.columns[0].note = Note("First column note")
        table1.columns[1].note = Note("Second column note")
        expected = (
            "\n"
            "\n"
            'COMMENT ON COLUMN "products"."id" IS \'First column note\';\n'
            "\n"
            'COMMENT ON COLUMN "products"."name" IS \'Second column note\';'
        )
        assert render_column_notes(table1) == expected

    @staticmethod
    def test_no_notes(table1: Table) -> None:
        assert render_column_notes(table1) == ""


def test_render_table(table1: Table) -> None:
    table1.note = Mock(sql="-- Simple note")
    with patch(
        "pydbml.renderer.sql.default.table.create_components",
        Mock(return_value="components"),
    ) as create_components_mock:
        with patch(
            "pydbml.renderer.sql.default.table.render_column_notes",
            Mock(return_value="\n\ncolumn notes"),
        ) as render_column_notes_mock:
            assert pydbml.renderer.sql.default.table.render_table(table1) == (
                "components\n\n-- Simple note\n\ncolumn notes"
            )
            assert create_components_mock.called
            assert render_column_notes_mock.called
