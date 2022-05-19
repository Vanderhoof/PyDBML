import pyparsing as pp

from .common import _
from .common import _c
from .common import end
from .generic import name
from pydbml.parser.blueprints import TableGroupBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

table_name = pp.Combine(name + '.' + name) | name

table_group = _c + (
    pp.CaselessLiteral('TableGroup')
    - name('name') + _
    - '{' + _
    - (table_name + _)[...]('items') + _
    - '}'
) + end


def parse_table_group(s, loc, tok):
    '''
    TableGroup tablegroup_name {
        table1
        table2
        table3
    }
    '''
    init_dict = {
        'name': tok['name'],
        'items': list(tok.get('items', []))
    }
    if 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment
    return TableGroupBlueprint(**init_dict)


table_group.set_parse_action(parse_table_group)
