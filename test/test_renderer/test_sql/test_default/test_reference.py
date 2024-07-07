import pytest

from pydbml.classes import Table, Reference
from pydbml.exceptions import TableNotFoundError
from pydbml.renderer.sql.default.reference import (
    validate_for_sql,
    col_names,
    generate_inline_sql,
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
            ) == expected
        )
