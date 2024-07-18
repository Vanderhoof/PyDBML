from unittest.mock import Mock, patch

from pydbml.renderer.dbml.default import DefaultDBMLRenderer


def test_render_db() -> None:
    db = Mock(
        project=Mock(),  # #1
        refs=(Mock(inline=False), Mock(inline=False), Mock(inline=True)),  # #2, #3
        tables=[Mock(), Mock(), Mock()],  # #4, #5, #6
        enums=[Mock(), Mock()],  # #7, #8
        table_groups=[Mock(), Mock()],  # #9, #10
        sticky_notes=[Mock(), Mock()],  # #11, #12
    )

    with patch.object(
        DefaultDBMLRenderer, "render", Mock(return_value="")
    ) as render_mock:
        DefaultDBMLRenderer.render_db(db)
        assert render_mock.call_count == 12
