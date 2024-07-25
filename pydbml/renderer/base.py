from typing import Type, Callable, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pydbml.database import Database


def unsupported_renderer(model) -> str:
    return ''


class BaseRenderer:
    _unsupported_renderer = unsupported_renderer

    @property
    def model_renderers(cls) -> Dict[Type, Callable]:
        """A class attribute dictionary to store the model renderers."""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def render(cls, model) -> str:
        """
        Render the model to a string. If the model is not supported, fall back to
        `self._unsupported_renderer` that by default returns an empty string.
        """

        return cls.model_renderers.get(type(model), cls._unsupported_renderer)(model)  # type: ignore

    @classmethod
    def renderer_for(cls, model_cls: Type) -> Callable:
        """A decorator to register a renderer for a model class."""
        def decorator(func) -> Callable:
            cls.model_renderers[model_cls] = func  # type: ignore
            return func
        return decorator

    @classmethod
    def render_db(cls, db: 'Database') -> str:
        raise NotImplementedError  # pragma: no cover
