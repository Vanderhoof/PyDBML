import pyparsing as pp

from .column import table_column, table_column_with_properties
from .common import _
from .common import _c
from .common import end
from .common import note
from .common import note_object
from .generic import name, string_literal
from .index import indexes
from pydbml.parser.blueprints import TableBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

alias = pp.WordStart() + pp.Literal('as').suppress() - pp.WordEnd() - name


hex_char = pp.Word(pp.srange('[0-9a-fA-F]'), exact=1)
hex_color = ("#" - (hex_char * 3 ^ hex_char * 6)).leaveWhitespace()
header_color = (
    pp.CaselessLiteral('headercolor:').suppress() + _
    - pp.Combine(hex_color)('header_color')
)
table_setting = _ + (note('note') | header_color) + _
table_settings = '[' + table_setting + (',' + table_setting)[...] + ']'


def parse_table_settings(s, loc, tok):
    '''
    [headercolor: #cccccc, note: 'note']
    '''
    result = {}
    if 'note' in tok:
        result['note'] = tok['note']
    if 'header_color' in tok:
        result['header_color'] = tok['header_color']
    return result


table_settings.set_parse_action(parse_table_settings)


note_element = note | note_object

prop = name + pp.Suppress(":") + string_literal

table_element = _ + (note_element('note') | indexes('indexes')) + _
table_element_with_property = _ + (note_element('note') | indexes('indexes') | prop.set_results_name('property', list_all_matches=True)) + _

table_body = table_column[1, ...]('columns') + _ + table_element[...]
table_body_with_properties = table_column_with_properties[1, ...]('columns') + _ + table_element_with_property[...]

table_name = (name('schema') + '.' + name('name')) | (name('name'))

table = _c + (
    pp.CaselessLiteral("table").suppress()
    + table_name
    + alias('alias')[0, 1]
    + table_settings('settings')[0, 1] + _
    + '{' - table_body + _ + '}'
) + end

table_with_properties = _c + (
    pp.CaselessLiteral("table").suppress()
    + table_name
    + alias('alias')[0, 1]
    + table_settings('settings')[0, 1] + _
    + '{' - table_body_with_properties + _ + '}'
) + end


def parse_table(s, loc, tok):
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
        'name': tok['name'],
    }
    if 'schema' in tok:
        init_dict['schema'] = tok['schema']
    if 'settings' in tok:
        init_dict.update(tok['settings'])
    if 'alias' in tok:
        init_dict['alias'] = tok['alias'][0]
    if 'note' in tok:
        # will override one from settings
        init_dict['note'] = tok['note'][0]
    if 'indexes' in tok:
        init_dict['indexes'] = tok['indexes']
    if 'columns' in tok:
        init_dict['columns'] = tok['columns']
    if 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment
    if 'property' in tok:
        init_dict['properties'] = {k: v for k, v in tok['property']}
    result = TableBlueprint(**init_dict)

    return result


table.set_parse_action(parse_table)
table_with_properties.set_parse_action(parse_table)
