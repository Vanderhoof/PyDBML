from textwrap import dedent
from unittest.mock import patch

import pytest

from pydbml.classes import Table, Reference
from pydbml.exceptions import TableNotFoundError
from pydbml.renderer.sql.default.reference import (
    validate_for_sql,
    col_names,
    generate_inline_sql,
    generate_not_inline_sql,
    generate_many_to_many_sql,
    render_reference,
)


def test_col_names(table1: Table) -> None:
    assert col_names(table1.columns) == '"id", "name"'


class TestValidateForSQL:
    @staticmethod
    def test_ok(reference1: Reference) -> None:
        validate_for_sql(reference1)

    @staticmethod
    def test_faulty(reference1: Reference) -> None:
        reference1.col2[0].table = None
        with pytest.raises(TableNotFoundError):
            validate_for_sql(reference1)


class TestGenerateInlineSQL:
    @staticmethod
    def test_simple(reference1: Reference) -> None:
        expected = '{c}FOREIGN KEY ("product_id") REFERENCES "products" ("id")'
        assert (
            generate_inline_sql(
                reference1, source_col=reference1.col1, ref_col=reference1.col2
            )
            == expected
        )

    @staticmethod
    def test_on_update_on_delete(reference1: Reference) -> None:
        reference1.on_update = "cascade"
        reference1.on_delete = "set null"
        expected = '{c}FOREIGN KEY ("product_id") REFERENCES "products" ("id") ON UPDATE CASCADE ON DELETE SET NULL'
        assert (
            generate_inline_sql(
                reference1, source_col=reference1.col1, ref_col=reference1.col2
            )
            == expected
        )


class TestGenerateNotInlineSQL:
    @staticmethod
    def test_simple(reference1: Reference) -> None:
        expected = 'ALTER TABLE "orders" ADD {c}FOREIGN KEY ("product_id") REFERENCES "products" ("id");'
        assert (
            generate_not_inline_sql(
                reference1, source_col=reference1.col1, ref_col=reference1.col2
            )
            == expected
        )

    @staticmethod
    def test_on_update_on_delete(reference1: Reference) -> None:
        reference1.on_update = "cascade"
        reference1.on_delete = "set null"
        expected = 'ALTER TABLE "orders" ADD {c}FOREIGN KEY ("product_id") REFERENCES "products" ("id") ON UPDATE CASCADE ON DELETE SET NULL;'
        assert (
            generate_not_inline_sql(
                reference1, source_col=reference1.col1, ref_col=reference1.col2
            )
            == expected
        )


def test_generate_many_to_many_sql(reference1: Reference) -> None:
    reference1.type = "<>"
    expected = dedent(
        """\
        CREATE TABLE "orders_products" (
          "orders_product_id" integer NOT NULL,
          "products_id" integer NOT NULL,
          PRIMARY KEY ("orders_product_id", "products_id")
        );
        
        ALTER TABLE "orders_products" ADD FOREIGN KEY ("orders_product_id") REFERENCES "orders" ("product_id");
        
        ALTER TABLE "orders_products" ADD FOREIGN KEY ("products_id") REFERENCES "products" ("id");"""
    )
    assert generate_many_to_many_sql(reference1) == expected


class TestRenderReference:
    @staticmethod
    def test_many_to_many(reference1: Reference) -> None:
        reference1.type = "<>"
        with patch(
            "pydbml.renderer.sql.default.reference.generate_many_to_many_sql"
        ) as mock:
            render_reference(reference1)
            mock.assert_called_once_with(reference1)

    @staticmethod
    def test_inline_to_one(reference1: Reference) -> None:
        reference1.type = ">"
        reference1.inline = True
        with patch("pydbml.renderer.sql.default.reference.generate_inline_sql") as mock:
            render_reference(reference1)
            mock.assert_called_once_with(
                model=reference1, source_col=reference1.col1, ref_col=reference1.col2
            )
            reference1.type = "-"
            render_reference(reference1)
            assert mock.call_count == 2

    @staticmethod
    def test_inline_to_many(reference1: Reference) -> None:
        reference1.type = "<"
        reference1.inline = True
        with patch("pydbml.renderer.sql.default.reference.generate_inline_sql") as mock:
            render_reference(reference1)
            mock.assert_called_once_with(
                model=reference1, source_col=reference1.col2, ref_col=reference1.col1
            )

    @staticmethod
    def test_not_inline_to_one(reference1: Reference) -> None:
        reference1.type = ">"
        reference1.inline = False
        with patch("pydbml.renderer.sql.default.reference.generate_not_inline_sql") as mock:
            render_reference(reference1)
            mock.assert_called_once_with(
                model=reference1, source_col=reference1.col1, ref_col=reference1.col2
            )
            reference1.type = "-"
            render_reference(reference1)
            assert mock.call_count == 2

    @staticmethod
    def test_not_inline_to_many(reference1: Reference) -> None:
        reference1.type = "<"
        reference1.inline = False
        with patch("pydbml.renderer.sql.default.reference.generate_not_inline_sql") as mock:
            render_reference(reference1)
            mock.assert_called_once_with(
                model=reference1, source_col=reference1.col2, ref_col=reference1.col1
            )
