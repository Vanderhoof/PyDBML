from pydbml.classes import Column, Expression, Index
from pydbml.renderer.sql.default.index import render_subject, render_index


class TestRenderSubject:
    @staticmethod
    def test_column(simple_column: Column) -> None:
        expected = '"id"'
        assert render_subject(simple_column) == expected

    @staticmethod
    def test_expression(expression1: Expression) -> None:
        expected = "(SUM(amount))"
        assert render_subject(expression1) == expected

    @staticmethod
    def test_other() -> None:
        expected = "test"
        assert render_subject(expected) == expected


class TestRenderIndex:
    @staticmethod
    def test_basic_sql(index1: Index) -> None:
        expected = 'CREATE INDEX ON "products" ("name");'
        assert render_index(index1) == expected
