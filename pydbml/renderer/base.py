from typing import Type, Callable, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from pydbml.database import Database


def unsupported_renderer(model) -> str:
    return ''


class BaseRenderer:
    @property
    def model_renderers(cls) -> Dict[Type, Callable]:
        raise NotImplementedError

    @classmethod
    def render(cls, model) -> str:
        return cls.model_renderers.get(type(model), unsupported_renderer)(model)

    @classmethod
    def renderer_for(cls, model_cls: Type) -> Callable:
        def decorator(func) -> Callable:
            cls.model_renderers[model_cls] = func
            return func
        return decorator

    @classmethod
    def render_db(cls, db: 'Database') -> str:
        raise NotImplementedError
