import re
from typing import TYPE_CHECKING

from pydbml.tools import comment

if TYPE_CHECKING:
    from pydbml.classes import Note


def prepare_text_for_dbml(text: str) -> str:
    '''Escape single quotes'''
    pattern = re.compile(r"('''|')")
    return pattern.sub(r'\\\1', text)


def quote_string(text: str) -> str:
    if '\n' in text:
        return f"'''\n{prepare_text_for_dbml(text)}'''"
    else:
        return f"'{prepare_text_for_dbml(text)}'"


def note_option_to_dbml(note: 'Note') -> str:
    if '\n' in note.text:
        return f"note: '''{prepare_text_for_dbml(note.text)}'''"
    else:
        return f"note: '{prepare_text_for_dbml(note.text)}'"


def comment_to_dbml(val: str) -> str:
    return comment(val, '//')
