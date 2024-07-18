from pydbml.renderer.base import BaseRenderer


class SampleRenderer(BaseRenderer):
    model_renderers = {}


def test_renderer_for() -> None:
    @SampleRenderer.renderer_for(str)
    def render_str(model):
        return 'str'

    assert len(SampleRenderer.model_renderers) == 1
    assert str in SampleRenderer.model_renderers
    assert SampleRenderer.model_renderers[str] is render_str


class TestRender:
    @staticmethod
    def test_render() -> None:
        @SampleRenderer.renderer_for(str)
        def render_str(model):
            return 'str'

        assert SampleRenderer.render('') == 'str'

    @staticmethod
    def test_render_not_supported() -> None:
        assert SampleRenderer.render(1) == ''

    @staticmethod
    def test_unsupported_renderer_override() -> None:
        def unsupported_renderer(model):
            return 'unsupported'

        class SampleRenderer2(BaseRenderer):
            model_renderers = {}
            _unsupported_renderer = unsupported_renderer

        assert SampleRenderer2.render(1) == 'unsupported'
