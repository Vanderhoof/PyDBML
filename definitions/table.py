import pyparsing as pp
from .generic import (expression, name, string_literal, boolean_literal,
                      number_literal)
from .common import note, comment, pk, unique, note_object
from .column import table_column

alias = pp.WordStart() + pp.Literal('as') + pp.WordEnd() + name


hex_char = pp.Word(pp.srange('[0-9a-fA-F]'), exact=1)
hex_color = ("#" + (hex_char * 3 ^ hex_char * 6)).leaveWhitespace()
header_color = pp.CaselessLiteral('headercolor:') + hex_color
table_setting = note | header_color
table_settings = '[' + table_setting + (',' + table_setting)[...] + ']'


index_setting = (
    unique |
    pp.CaselessLiteral("type:") + (pp.CaselessLiteral("btree") | pp.CaselessLiteral("hash")) |
    pp.CaselessLiteral("name:") + string_literal
)
index_settings = (
    '[' + pk + ']' | '[' + index_setting + (',' + index_setting)[...] + ']'
)
single_index = name | expression
composite_index_syntax = '(' + single_index + (',' + single_index)[...] + ')' + index_settings
single_index_syntax = single_index + index_settings
indexes_body = single_index_syntax | composite_index_syntax
indexes = pp.CaselessLiteral('indexes') + '{' + indexes_body + '}'
table_element = note_object | indexes

table_body = table_column[1, ...] + table_element[...]

table = pp.CaselessLiteral("table") + name + alias[0, 1] + table_settings[0, 1] + '{' + table_body + '}'
