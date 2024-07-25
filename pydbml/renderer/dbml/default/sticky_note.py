from textwrap import indent


from pydbml.classes import StickyNote
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import quote_string


@DefaultDBMLRenderer.renderer_for(StickyNote)
def render_sticky_note(model: StickyNote) -> str:
    text = quote_string(model.text)

    text = indent(text, '    ')
    result = f'Note {model.name} {{\n{text}\n}}'
    return result
