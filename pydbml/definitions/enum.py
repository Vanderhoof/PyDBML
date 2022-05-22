import pyparsing as pp

from .common import _
from .common import _c
from .common import c
from .common import end
from .common import n
from .common import note
from .generic import name
from pydbml.parser.blueprints import EnumBlueprint
from pydbml.parser.blueprints import EnumItemBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

enum_settings = '[' + _ - note('note') + _ - ']' + c


def parse_enum_settings(s, loc, tok):
    '''
    [note: "note content"] // comment
    '''
    result = {}
    if 'note' in tok:
        result['note'] = tok['note']
    if 'comment' in tok:
        result['comment'] = tok['comment'][0]
    return result


enum_settings.set_parse_action(parse_enum_settings)

enum_item = _c + (name('name') + c + enum_settings('settings')[0, 1])


def parse_enum_item(s, loc, tok):
    '''
    student [note: "is stupid"]
    '''
    init_dict = {'name': tok['name']}
    if 'settings' in tok:
        init_dict.update(tok['settings'])
        # comments after settings have priority
        if 'comment' in tok['settings']:
            init_dict['comment'] = tok['settings']['comment']
    if 'comment' not in init_dict and 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment

    return EnumItemBlueprint(**init_dict)


enum_item.set_parse_action(parse_enum_item)

enum_body = enum_item[1, ...]

enum_name = pp.Combine(name("schema") + '.' + name("name")) | name("name")

enum = _c + (
    pp.CaselessLiteral('enum')
    - enum_name + _
    - '{'
    + enum_body('items') + n
    - '}'
) + end


def parse_enum(s, loc, tok):
    '''
    enum members {
        janitor
        student
        teacher
        headmaster
    }
    '''
    init_dict = {
        'name': tok['name'],
        'items': list(tok['items'])
    }

    if 'schema' in tok:
        init_dict['schema'] = tok['schema']

    if 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment

    return EnumBlueprint(**init_dict)


enum.set_parse_action(parse_enum)
