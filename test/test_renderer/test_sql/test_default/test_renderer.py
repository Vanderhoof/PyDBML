from unittest.mock import Mock, patch

from pydbml.renderer.sql.default import DefaultSQLRenderer


def test_render() -> None:
    model = Mock()
    result = DefaultSQLRenderer.render(model)
    assert model.check_attributes_for_sql.called
    assert result == ""


def test_render_db() -> None:
    db = Mock(
        refs=(Mock(inline=False), Mock(inline=False), Mock(inline=True)),
        tables=[Mock(), Mock(), Mock()],
        enums=[Mock(), Mock()],
    )

    with patch(
        "pydbml.renderer.sql.default.renderer.reorder_tables_for_sql",
        Mock(return_value=db.tables),
    ) as reorder_mock:
        with patch.object(
            DefaultSQLRenderer, "render", Mock(return_value="")
        ) as render_mock:
            result = DefaultSQLRenderer.render_db(db)
            assert reorder_mock.called
            assert render_mock.call_count == 7
