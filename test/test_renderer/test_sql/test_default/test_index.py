from pydbml.classes import Column, Expression, Index
from pydbml.renderer.sql.default.index import render_subject, render_index, render_pk


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


class TestRenderPK:
    @staticmethod
    def test_comment(index1: Index) -> None:
        index1.comment = "Test comment"
        expected = '-- Test comment\nPRIMARY KEY ("name")'
        assert render_pk(index1, '"name"') == expected

    @staticmethod
    def test_no_comment(index1: Index) -> None:
        expected = 'PRIMARY KEY ("name")'
        assert render_pk(index1, '"name"') == expected


class TestRenderComponents:
    @staticmethod
    def test_comment(index1: Index) -> None:
        index1.comment = "Test comment"
        expected = '-- Test comment\nCREATE INDEX ON "products" ("name");'
        assert render_index(index1) == expected

    @staticmethod
    def test_unique(index1: Index) -> None:
        index1.unique = True
        expected = 'CREATE UNIQUE INDEX ON "products" ("name");'
        assert render_index(index1) == expected

    @staticmethod
    def test_name(index1: Index) -> None:
        index1.name = "test"
        expected = 'CREATE INDEX "test" ON "products" ("name");'
        assert render_index(index1) == expected

    @staticmethod
    def test_no_table(index1: Index) -> None:
        index1.table = None
        expected = 'CREATE INDEX ("name");'
        assert render_index(index1) == expected

    @staticmethod
    def test_type(index1: Index) -> None:
        index1.type = "hash"
        expected = 'CREATE INDEX ON "products" USING HASH ("name");'
        assert render_index(index1) == expected


class TestRenderIndex:
    @staticmethod
    def test_render_index(index1: Index) -> None:
        index1.comment = "Test comment"
        index1.unique = True
        index1.name = "test"
        index1.type = "hash"

        expected = '-- Test comment\nCREATE UNIQUE INDEX "test" ON "products" USING HASH ("name");'
        assert render_index(index1) == expected

    @staticmethod
    def test_render_pk(index1: Index) -> None:
        index1.pk = True
        expected = 'PRIMARY KEY ("name")'
        assert render_index(index1) == expected
