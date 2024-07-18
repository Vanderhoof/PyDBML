import re
from textwrap import indent

from pydbml.classes import Note
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer


def prepare_text_for_dbml(model):
    '''Escape single quotes'''
    pattern = re.compile(r"('''|')")
    return pattern.sub(r'\\\1', model.text)


@DefaultDBMLRenderer.renderer_for(Note)
def render_note(model: Note) -> str:
    text = prepare_text_for_dbml(model)
    if '\n' in text:
        note_text = f"'''\n{text}\n'''"
    else:
        note_text = f"'{text}'"

    note_text = indent(note_text, '    ')
    result = f'Note {{\n{note_text}\n}}'
    return result
