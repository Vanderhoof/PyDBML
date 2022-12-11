import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .classes import Note


def comment(val: str, comb: str) -> str:
    return '\n'.join(f'{comb} {cl}' for cl in val.split('\n')) + '\n'


def comment_to_dbml(val: str) -> str:
    return comment(val, '//')


def comment_to_sql(val: str) -> str:
    return comment(val, '--')


def note_option_to_dbml(note: 'Note') -> str:
    if '\n' in note.text:
        return f"note: '''{note._prepare_text_for_dbml()}'''"
    else:
        return f"note: '{note._prepare_text_for_dbml()}'"


def indent(val: str, spaces=4) -> str:
    if val == '':
        return val
    return ' ' * spaces + val.replace('\n', '\n' + ' ' * spaces)


def remove_bom(source: str) -> str:
    if source and source[0] == '\ufeff':
        source = source[1:]
    return source


def strip_empty_lines(source: str) -> str:
    """Remove empty lines or lines with just spaces from beginning and end."""
    pattern = re.compile(r'^([ \t]*\n)*(?P<content>[\s\S]+?)(\n[ \t]*)*$')
    return pattern.sub('\g<content>', source)


def remove_indentation(source: str) -> str:
    if not source:
        return source

    pattern = re.compile(r'^\s*')

    lines = source.split('\n')
    spaces = []
    for line in lines:
        if line and not line.isspace():
            indent_match = pattern.search(line)
            if indent_match is not None:  # this is just for you mypy
                spaces.append(len(indent_match[0]))

    indent = min(spaces)
    lines = [l[indent:] for l in lines]
    return '\n'.join(lines)
