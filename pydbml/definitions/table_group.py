import pyparsing as pp
from pydbml.definitions.generic import name
from pydbml.definitions.common import _, __, _c, n
from pydbml.classes import TableGroup

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

tg_body = name + __

table_group = _c + (
    pp.CaselessLiteral('TableGroup') +
    name('name') + _ +
    '{' + _ +
    tg_body[...]('items') + _ +
    '}'
) + (n | pp.StringEnd())


def parse_table_group(s, l, t):
    init_dict = {
        'name': t['name'],
        'items': list(t['items'])
    }
    if 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment
    return TableGroup(**init_dict)


table_group.setParseAction(parse_table_group)
