from typing import TYPE_CHECKING

from pydbml.renderer.sql.default.utils import reorder_tables_for_sql
from pydbml.renderer.base import BaseRenderer


if TYPE_CHECKING:  # pragma: no cover
    from pydbml.database import Database


class DefaultSQLRenderer(BaseRenderer):
    model_renderers = {}

    @classmethod
    def render(cls, model) -> str:
        model.check_attributes_for_sql()
        return super().render(model)

    @classmethod
    def render_db(cls, db: 'Database') -> str:
        refs = (ref for ref in db.refs if not ref.inline)
        tables = reorder_tables_for_sql(db.tables, db.refs)
        components = (cls.render(i) for i in (*db.enums, *tables, *refs))
        return '\n\n'.join(components)
