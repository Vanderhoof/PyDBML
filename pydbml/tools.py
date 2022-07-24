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


def strip_empty_lines(source: str) -> str:
    """Remove empty lines or lines with just spaces from beginning and end."""
    first_line = 0
    lines = source.split('\n')
    last_line = len(lines) - 1
    while not lines[first_line] or lines[first_line].isspace():
        first_line += 1
    while not lines[last_line] or lines[last_line].isspace():
        last_line -= 1
    return '\n'.join(lines[first_line: last_line + 1])


def remove_indentation(source: str) -> str:
    pattern = re.compile(r'^\s*')

    lines = source.split('\n')
    spaces = []
    for line in lines:
        if line and not line.isspace():
            spaces.append(len(pattern.search(line).group()))

    indent = min(spaces)
    lines = [l[indent:] for l in lines]
    return '\n'.join(lines)

def reformat_note_text(source: str, spaces=4) -> str:
    """
    Add line breaks at approx 80-90 characters.
    If source is less than 90 characters and has no line breaks, leave it unchanged.
    """
    if '\n' not in source and len(source) <= 90:
        return f"'{source}'"

    lines = []
    line = ''
    text = remove_indentation(source.strip('\n'))
    for word in text.split(' '):
        if len(line) > 80:
            lines.append(line)
            line = ''
        if '\n' in word:
            sublines = word.split('\n')
            for sl in sublines[:-1]:
                line += sl
                lines.append(line)
                line = ''
            line = sublines[-1] + ' '
        else:
            line += f'{word} '
    if line:
        lines.append(line)
    result = '\n'.join(lines).rstrip()
    result = f"'''\n{result}\n'''"

    return f'{result}'
