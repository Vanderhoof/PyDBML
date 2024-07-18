from pydbml.renderer.dbml.default.note import prepare_text_for_dbml
from pydbml.tools import comment


def note_option_to_dbml(note: 'Note') -> str:
    if '\n' in note.text:
        return f"note: '''{prepare_text_for_dbml(note)}'''"
    else:
        return f"note: '{prepare_text_for_dbml(note)}'"


def comment_to_dbml(val: str) -> str:
    return comment(val, '//')
