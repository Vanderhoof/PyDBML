from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Callable, Dict, Type

if TYPE_CHECKING:  # pragma: no cover
    from pydbml.database import Database


def unsupported_renderer(model) -> str:
    return ''


class BaseRenderer(ABC):
    _unsupported_renderer = unsupported_renderer

    model_renderers: ClassVar[Dict[Type, Callable]]

    @classmethod
    def render(cls, model) -> str:
        """
        Render the model to a string. If the model is not supported, fall back to
        `_unsupported_renderer` that by default returns an empty string.
        """
        return cls.model_renderers.get(type(model), cls._unsupported_renderer)(model)

    @classmethod
    def renderer_for(cls, model_cls: Type) -> Callable:
        """A decorator to register a renderer for a model class."""
        def decorator(func) -> Callable:
            cls.model_renderers[model_cls] = func
            return func
        return decorator

    @classmethod
    def render_db(cls, db: 'Database') -> str:
        raise NotImplementedError  # pragma: no cover
