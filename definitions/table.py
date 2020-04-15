import pyparsing as pp
from definitions.generic import name
from definitions.common import note, note_object, comment
from definitions.column import table_column
from definitions.index import index
from classes import Table

alias = pp.WordStart() + pp.Literal('as').suppress() + pp.WordEnd() + name


hex_char = pp.Word(pp.srange('[0-9a-fA-F]'), exact=1)
hex_color = ("#" + (hex_char * 3 ^ hex_char * 6)).leaveWhitespace()
header_color = (
    pp.CaselessLiteral('headercolor:').suppress() +
    pp.White()[...].suppress() +
    pp.Combine(hex_color)
)
table_setting = note('note') | header_color('header_color')
table_settings = '[' + table_setting + (',' + table_setting)[...] + ']'


def parse_table_settings(s, l, t):
    result = {}
    if 'note' in t:
        result['note'] = t['note']
    if 'header_color' in t:
        result['header_color'] = t['header_color']
    return result


table_settings.addParseAction(parse_table_settings)


indexes = (
    pp.CaselessLiteral('indexes').suppress() +
    pp.Suppress('{') +
    index[1, ...] +
    pp.Suppress('}')
)

note_element = note | note_object

table_element = note_element('note') | indexes('indexes')

table_body = table_column[1, ...]('columns') + table_element[...]

table = (
    pp.CaselessLiteral("table").suppress() +
    name('name') +
    alias('alias')[0, 1] +
    table_settings('settings')[0, 1] +
    '{' + table_body + '}'
)


def parse_table(s, l, t):
    init_dict = {
        'name': t['name'],
        'columns': list(t['columns'])
    }
    if 'settings' in t:
        init_dict.update(t['settings'])
    if 'alias' in t:
        init_dict['alias'] = t['alias']
    if 'indexes' in t:
        init_dict['indexes'] = list(t['indexes'])
    if 'note' in t:
        # will override one from settings
        init_dict['note'] = t['note']
    return Table(**init_dict)


table.addParseAction(parse_table)
table.ignore(comment)
