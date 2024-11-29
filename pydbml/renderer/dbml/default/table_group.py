from pydbml.classes import TableGroup
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.table import get_full_name_for_dbml
from pydbml.renderer.dbml.default.utils import comment_to_dbml


@DefaultDBMLRenderer.renderer_for(TableGroup)
def render_table_group(model: TableGroup) -> str:
    result = comment_to_dbml(model.comment) if model.comment else ''
    result += f'TableGroup "{model.name}" {{\n'
    for i in model.items:
        result += f'    {get_full_name_for_dbml(i)}\n'
    result += '}'
    return result
