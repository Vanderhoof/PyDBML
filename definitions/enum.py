import pyparsing as pp
from definitions.generic import name
from definitions.common import _, note
from classes import EnumItem, Enum


enum_setting = _ + note('note') + _

enum_settings = '[' + enum_setting + ']'


def parse_enum_settings(s, l, t):
    result = {}
    if 'note' in t:
        result['note'] = t['note']
    return result


enum_settings.setParseAction(parse_enum_settings)

enum_item = _ + (name('name') + enum_settings('settings')[0, 1]) + _


def parse_enum_item(s, l, t):
    init_dict = {'name': t['name']}
    if 'settings' in t:
        init_dict.update(t['settings'])
    return EnumItem(init_dict)


enum_item.setParseAction(parse_enum_item)

enum_body = enum_item[1, ...]

enum = (
    pp.CaselessLiteral('enum') +
    name('name') + _ +
    '{' + _ +
    enum_body('items') + _ +
    '}'
)


def parse_enum(s, l, t):
    return Enum(name=t['name'], items=list(t['items']))


enum.setParseAction(parse_enum)
