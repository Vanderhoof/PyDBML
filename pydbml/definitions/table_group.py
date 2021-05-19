import pyparsing as pp

from pydbml.classes import TableGroup

from .common import _
from .common import _c
from .common import end
from .generic import name

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

table_group = _c + (
    pp.CaselessLiteral('TableGroup')
    - name('name') + _
    - '{' + _
    - (name + _)[...]('items') + _
    - '}'
) + end


def parse_table_group(s, l, t):
    '''
    TableGroup tablegroup_name {
        table1
        table2
        table3
    }
    '''
    init_dict = {
        'name': t['name'],
        'items': list(t.get('items', []))
    }
    if 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment
    return TableGroup(**init_dict)


table_group.setParseAction(parse_table_group)
