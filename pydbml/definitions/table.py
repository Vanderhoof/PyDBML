import pyparsing as pp

from pydbml.classes import Table

from .column import table_column
from .common import _
from .common import _c
from .common import end
from .common import note
from .common import note_object
from .generic import name
from .index import indexes

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

alias = pp.WordStart() + pp.Literal('as').suppress() - pp.WordEnd() - name


hex_char = pp.Word(pp.srange('[0-9a-fA-F]'), exact=1)
hex_color = ("#" - (hex_char * 3 ^ hex_char * 6)).leaveWhitespace()
header_color = (
    pp.CaselessLiteral('headercolor:').suppress() + _
    - pp.Combine(hex_color)('header_color')
)
table_setting = _ + (note('note') | header_color) + _
table_settings = '[' + table_setting + (',' + table_setting)[...] + ']'


def parse_table_settings(s, l, t):
    '''
    [headercolor: #cccccc, note: 'note']
    '''
    result = {}
    if 'note' in t:
        result['note'] = t['note']
    if 'header_color' in t:
        result['header_color'] = t['header_color']
    return result


table_settings.setParseAction(parse_table_settings)


note_element = note | note_object

table_element = _ + (note_element('note') | indexes('indexes')) + _

table_body = table_column[1, ...]('columns') + _ + table_element[...]

table = _c + (
    pp.CaselessLiteral("table").suppress()
    + name('name')
    + alias('alias')[0, 1]
    + table_settings('settings')[0, 1] + _
    + '{' - table_body + _ + '}'
) + end


def parse_table(s, l, t):
    '''
    Table bookings as bb [headercolor: #cccccc] {
      id integer
      country varchar [NOT NULL, ref: > countries.country_name]
      booking_date date unique pk
      created_at timestamp

      indexes {
          (id, country) [pk] // composite primary key
      }
    }
    '''
    init_dict = {
        'name': t['name'],
    }
    if 'settings' in t:
        init_dict.update(t['settings'])
    if 'alias' in t:
        init_dict['alias'] = t['alias'][0]
    if 'note' in t:
        # will override one from settings
        init_dict['note'] = t['note'][0]
    if'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment
    result = Table(**init_dict)
    for column in t['columns']:
        result.add_column(column)
    for index_ in t.get('indexes', []):
        result.add_index(index_)

    return result


table.setParseAction(parse_table)
