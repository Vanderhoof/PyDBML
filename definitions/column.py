import pyparsing as pp
from definitions.generic import (expression, name, string_literal, boolean_literal,
                                 number_literal)
from definitions.common import note, comment, pk, unique
from classes import ColumnType


def parse_column_type(s, l, t):
    return ColumnType(name=t['name'],
                      args=t.get('args'))


type_args = ("(" + pp.originalTextFor(expression)('args') + ")")
type_name = (pp.Word(pp.alphanums + '_[]') | pp.dblQuotedString())('name')
column_type = (type_name + type_args[0, 1]).setParseAction(parse_column_type)


relation = pp.oneOf(">-<")
ref_inline = pp.Literal("ref:") + relation + name + '.' + name
default = pp.CaselessLiteral('default:') + (
    string_literal | expression | boolean_literal | number_literal
)
column_setting = (
    pp.CaselessLiteral("not null") |
    pp.CaselessLiteral("null") |
    pp.CaselessLiteral("primary key") |
    pk |
    unique |
    pp.CaselessLiteral("increment") |
    note |
    ref_inline |
    default

)
column_settings = '[' + column_setting + ("," + column_setting)[...] + ']'

constraint = pp.CaselessLiteral("unique") | pp.CaselessLiteral("pk")

table_column = (
    name('name') +
    column_type('type') +
    constraint[...]('constraints') +
    column_settings[0, 1]('settings') +
    comment[0, 1]('comment')
)

