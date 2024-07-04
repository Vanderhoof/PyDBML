from typing import TYPE_CHECKING, List

from pydbml.renderer.base import BaseRenderer

if TYPE_CHECKING:
    from pydbml.database import Database


class DefaultDBMLRenderer(BaseRenderer):
    model_renderers = {}

    @classmethod
    def render_db(cls, db: 'Database') -> str:
        items: List[DBMLOBject] = [db.project] if db.project else []
        refs = (ref for ref in db.refs if not ref.inline)
        items.extend((*db.enums, *db.tables, *refs, *db.table_groups, *db.sticky_notes))

        return '\n\n'.join(cls.render(i) for i in items)
