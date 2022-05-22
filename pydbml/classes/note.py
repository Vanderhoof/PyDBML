from typing import Any

from .base import SQLObject


class Note(SQLObject):
    def __init__(self, text: Any):
        self.text = str(text) if text else ''

    def __str__(self):
        '''
        >>> print(Note('Note text'))
        Note text
        '''

        return self.text

    def __bool__(self):
        return bool(self.text)

    def __repr__(self):
        '''
        >>> Note('Note text')
        Note('Note text')
        '''

        return f'Note({repr(self.text)})'

    @property
    def sql(self):
        if self.text:
            return '\n'.join(f'-- {line}' for line in self.text.split('\n'))
        else:
            return ''

    @property
    def dbml(self):
        lines = []
        line = ''
        for word in self.text.split(' '):
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
        result = 'Note {\n    '

        if len(lines) > 1:
            lines_str = '\n    '.join(lines)[:-1] + '\n'
            result += f"'''\n    {lines_str}    '''"
        else:
            result += f"'{lines[0][:-1]}'"

        result += '\n}'
        return result
