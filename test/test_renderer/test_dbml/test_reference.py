from unittest.mock import patch

import pytest

from pydbml._classes.reference import Reference
from pydbml.exceptions import TableNotFoundError, DBMLError
from pydbml.renderer.dbml.default.reference import (
    validate_for_dbml,
    render_inline_reference,
    render_col,
    render_options,
    render_not_inline_reference,
    render_reference,
)


class TestValidateFroDBML:
    @staticmethod
    def test_ok(reference1: Reference) -> None:
        validate_for_dbml(reference1)

    @staticmethod
    def test_no_table(reference1: Reference) -> None:
        reference1.col2[0].table = None
        with pytest.raises(TableNotFoundError):
            validate_for_dbml(reference1)


class TestRenderInlineReference:
    @staticmethod
    def test_ok(reference1: Reference) -> None:
        reference1.inline = True
        assert render_inline_reference(reference1) == 'ref: > "products"."id"'

    @staticmethod
    def test_composite(reference1: Reference) -> None:
        reference1.col2.append(reference1.col2[0])
        with pytest.raises(DBMLError):
            render_inline_reference(reference1)


class TestRendeCol:
    @staticmethod
    def test_single(reference1: Reference) -> None:
        assert render_col(reference1.col2) == '"id"'

    @staticmethod
    def test_multiple(reference1: Reference) -> None:
        reference1.col2.append(reference1.col2[0])
        assert render_col(reference1.col2) == '("id", "id")'


class TestRenderOptions:
    @staticmethod
    def test_on_update(reference1: Reference) -> None:
        reference1.on_update = "cascade"
        assert render_options(reference1) == " [update: cascade]"

    @staticmethod
    def test_on_delete(reference1: Reference) -> None:
        reference1.on_delete = "set null"
        assert render_options(reference1) == " [delete: set null]"

    @staticmethod
    def test_both(reference1: Reference) -> None:
        reference1.on_update = "cascade"
        reference1.on_delete = "set null"
        assert render_options(reference1) == " [update: cascade, delete: set null]"

    @staticmethod
    def test_no_options(reference1: Reference) -> None:
        assert render_options(reference1) == ""


class TestRenderNotInlineReference:
    @staticmethod
    def test_ok(reference1: Reference) -> None:
        assert render_not_inline_reference(reference1) == (
            'Ref {\n    "orders"."product_id" > "products"."id"\n}'
        )

    @staticmethod
    def test_comment(reference1: Reference) -> None:
        reference1.comment = "comment"
        assert render_not_inline_reference(reference1) == (
            '// comment\nRef {\n    "orders"."product_id" > "products"."id"\n}'
        )

    @staticmethod
    def test_name(reference1: Reference) -> None:
        reference1.name = "ref_name"
        assert render_not_inline_reference(reference1) == (
            'Ref ref_name {\n    "orders"."product_id" > "products"."id"\n}'
        )


class TestRenderReference:
    @staticmethod
    def test_inline(reference1: Reference) -> None:
        reference1.inline = True
        with patch(
            "pydbml.renderer.dbml.default.reference.render_inline_reference",
            return_value="inline",
        ) as mock_render:
            with patch(
                "pydbml.renderer.dbml.default.reference.validate_for_dbml",
            ) as mock_validate:
                assert render_reference(reference1) == "inline"
                assert mock_render.called
                assert mock_validate.called

    @staticmethod
    def test_not_inline(reference1: Reference) -> None:
        with patch(
            "pydbml.renderer.dbml.default.reference.render_not_inline_reference",
            return_value="not inline",
        ) as mock_render:
            with patch(
                "pydbml.renderer.dbml.default.reference.validate_for_dbml",
            ) as mock_validate:
                assert render_reference(reference1) == "not inline"
                assert mock_render.called
                assert mock_validate.called
