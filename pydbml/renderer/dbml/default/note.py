from textwrap import indent

from pydbml.classes import Note
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import quote_string


@DefaultDBMLRenderer.renderer_for(Note)
def render_note(model: Note) -> str:
    text = quote_string(model.text)

    text = indent(text, '    ')
    result = f'Note {{\n{text}\n}}'
    return result
