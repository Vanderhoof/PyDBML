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

def remove_indentation(source: str) -> str:
    pattern = re.compile(r'(?<=\n)\s*')
    spaces = pattern.findall(f'\n{source}')
    if not spaces:
        return source
    indent = min(map(len, spaces))
    lines = source.split('\n')
    lines = [l[indent:] for l in lines]
    return '\n'.join(lines)

def reformat_note_text(source: str, spaces=4) -> str:
    """
    Add line breaks at approx 80-90 characters, indent text.
    If source is less than 90 characters and has no line breaks, leave it unchanged.
    """
    if '\n' not in source and len(source) <= 90:
        return f"'{source}'"

    # text = source.strip('\n')
    lines = []
    line = ''
    for word in source.split(' '):
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
    # result = indent((result))
    return f'{result}'
