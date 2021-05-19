import pyparsing as pp

from pydbml.classes import Enum
from pydbml.classes import EnumItem

from .common import _
from .common import _c
from .common import c
from .common import end
from .common import n
from .common import note
from .generic import name

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

enum_settings = '[' + _ - note('note') + _ - ']' + c


def parse_enum_settings(s, l, t):
    '''
    [note: "note content"] // comment
    '''
    result = {}
    if 'note' in t:
        result['note'] = t['note']
    if 'comment' in t:
        result['comment'] = t['comment'][0]
    return result


enum_settings.setParseAction(parse_enum_settings)

enum_item = _c + (name('name') + c + enum_settings('settings')[0, 1])


def parse_enum_item(s, l, t):
    '''
    student [note: "is stupid"]
    '''
    init_dict = {'name': t['name']}
    if 'settings' in t:
        init_dict.update(t['settings'])

    # comments after settings have priority
    if 'comment' in t:
        init_dict['comment'] = t['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment

    return EnumItem(**init_dict)


enum_item.setParseAction(parse_enum_item)

enum_body = enum_item[1, ...]

enum = _c + (
    pp.CaselessLiteral('enum')
    - name('name') + _
    - '{'
    + enum_body('items') + n
    - '}'
) + end


def parse_enum(s, l, t):
    '''
    enum members {
        janitor
        student
        teacher
        headmaster
    }
    '''
    init_dict = {
        'name': t['name'],
        'items': list(t['items'])
    }

    if 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment

    return Enum(**init_dict)


enum.setParseAction(parse_enum)
