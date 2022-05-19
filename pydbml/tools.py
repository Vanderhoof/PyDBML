from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .classes import Note


def comment(val: str, comb: str) -> str:
    return '\n'.join(f'{comb} {cl}' for cl in val.split('\n')) + '\n'


def comment_to_dbml(val: str) -> str:
    return comment(val, '//')


def comment_to_sql(val: str) -> str:
    return comment(val, '--')


def note_option_to_dbml(val: 'Note') -> str:
    if '\n' in val.text:
        return f"note: '''{val.text}'''"
    else:
        return f"note: '{val.text}'"


def indent(val: str, spaces=4) -> str:
    if val == '':
        return val
    return ' ' * spaces + val.replace('\n', '\n' + ' ' * spaces)


def remove_bom(source: str) -> str:
    if source and source[0] == '\ufeff':
        source = source[1:]
    return source
