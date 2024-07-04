from pydbml.tools import comment


def note_option_to_dbml(note: 'Note') -> str:
    if '\n' in note.text:
        return f"note: '''{note._prepare_text_for_dbml()}'''"
    else:
        return f"note: '{note._prepare_text_for_dbml()}'"


def comment_to_dbml(val: str) -> str:
    return comment(val, '//')
