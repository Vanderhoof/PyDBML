from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .classes import Note

def comment_to_dbml(val: str) -> str:
    return '\n'.join(f'// {cl}' for cl in val.split('\n')) + '\n'


def comment_to_sql(val: str) -> str:
    return '\n'.join(f'-- {cl}' for cl in val.split('\n')) + '\n'


def note_option_to_dbml(val: 'Note') -> str:
    if '\n' in val.text:
        return f"note: '''{val.text}'''"
    else:
        return f"note: '{val.text}'"


def indent(val: str, spaces=4) -> str:
    if val == '':
        return val
    return ' ' * spaces + val.replace('\n', '\n' +' ' * spaces)