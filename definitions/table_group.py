import pyparsing as pp
from definitions.generic import name
from definitions.common import _, __
from classes import TableGroup


tg_body = name + __

table_group = (
    pp.CaselessLiteral('TableGroup') +
    name('name') + _ +
    '{' + _ +
    tg_body('items') + _ +
    '}'
)


def parse_table_group(s, l, t):
    return TableGroup(name=t['name'], items=list(t['items']))


table_group.setParseAction(parse_table_group)
