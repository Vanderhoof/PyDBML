import pyparsing as pp
from pydbml.definitions.generic import name
from pydbml.definitions.common import _, note, note_object
from pydbml.definitions.column import table_column
from pydbml.definitions.index import index
from pydbml.classes import Table

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

alias = pp.WordStart() + pp.Literal('as').suppress() + pp.WordEnd() + name


hex_char = pp.Word(pp.srange('[0-9a-fA-F]'), exact=1)
hex_color = ("#" + (hex_char * 3 ^ hex_char * 6)).leaveWhitespace()
header_color = (
    pp.CaselessLiteral('headercolor:').suppress() + _ +
    pp.Combine(hex_color)('header_color')
)
table_setting = _ + (note('note') | header_color) + _
table_settings = '[' + table_setting + (',' + table_setting)[...] + ']'


def parse_table_settings(s, l, t):
    result = {}
    if 'note' in t:
        result['note'] = t['note']
    if 'header_color' in t:
        result['header_color'] = t['header_color']
    return result


table_settings.setParseAction(parse_table_settings)


indexes = (
    pp.CaselessLiteral('indexes').suppress() + _ +
    pp.Suppress('{') +
    index[1, ...] +
    pp.Suppress('}')
)

note_element = note | note_object

table_element = _ + (note_element('note') | indexes('indexes')) + _

table_body = _ + table_column[1, ...]('columns') + _ + table_element[...]

table = (
    pp.CaselessLiteral("table").suppress() +
    name('name') +
    alias('alias')[0, 1] +
    table_settings('settings')[0, 1] + _ +
    '{' + _ + table_body + _ + '}' + _
)


def parse_table(s, l, t):
    init_dict = {
        'name': t['name'],
    }
    if 'settings' in t:
        init_dict.update(t['settings'])
    if 'alias' in t:
        init_dict['alias'] = t['alias']
    if 'note' in t:
        # will override one from settings
        init_dict['note'] = t['note']
    result = Table(**init_dict)
    for column in t['columns']:
        result.add_column(column)
    for index_ in t.get('indexes', []):
        result.add_index(index_)

    return result


table.setParseAction(parse_table)
