import pyparsing as pp

from pydbml.classes import Column

from .common import _
from .common import _c
from .common import c
from .common import n
from .common import note
from .common import pk
from .common import unique
from .generic import boolean_literal
from .generic import expression
from .generic import expression_literal
from .generic import name
from .generic import number_literal
from .generic import string_literal
from .reference import ref_inline


pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

type_args = ("(" + pp.originalTextFor(expression)('args') + ")")
type_name = (pp.Word(pp.alphanums + '_') | pp.dblQuotedString())('name')
column_type = (type_name + type_args[0, 1])


def parse_column_type(s, l, t):
    '''
    int or "mytype" or varchar(255)
    '''
    result = t['name']
    args = t.get('args')
    result += '(' + args + ')' if args else ''
    return result


column_type.setParseAction(parse_column_type)


default = pp.CaselessLiteral('default:').suppress() + _ - (
    string_literal
    | expression_literal
    | boolean_literal.setParseAction(
        lambda s, l, t: {
            'true': True,
            'false': False,
            'NULL': None
        }[t[0]]
    )
    | number_literal.setParseAction(
        lambda s, l, t: float(''.join(t[0])) if '.' in t[0] else int(t[0])
    )
)


column_setting = _ + (
    pp.CaselessLiteral("not null").setParseAction(
        lambda s, l, t: True
    )('notnull')
    | pp.CaselessLiteral("null").setParseAction(
        lambda s, l, t: False
    )('notnull')
    | pp.CaselessLiteral("primary key")('pk')
    | pk('pk')
    | unique('unique')
    | pp.CaselessLiteral("increment")('increment')
    | note('note')
    | ref_inline('ref*')
    | default('default')
) + _
column_settings = '[' - column_setting + ("," + column_setting)[...] + ']' + c


def parse_column_settings(s, l, t):
    '''
    [ NOT NULL, increment, default: `now()`]
    '''
    result = {}
    if t.get('notnull'):
        result['not_null'] = True
    if 'pk' in t:
        result['pk'] = True
    if 'unique' in t:
        result['unique'] = True
    if 'increment' in t:
        result['autoinc'] = True
    if 'note' in t:
        result['note'] = t['note']
    if 'default' in t:
        result['default'] = t['default'][0]
    if 'ref' in t:
        result['ref_blueprints'] = list(t['ref'])
    if 'comment' in t:
        result['comment'] = t['comment'][0]
    return result


column_settings.setParseAction(parse_column_settings)


constraint = pp.CaselessLiteral("unique") | pp.CaselessLiteral("pk")

table_column = _c + (
    name('name')
    + column_type('type')
    + constraint[...]('constraints') + c
    + column_settings('settings')[0, 1]
) + n


def parse_column(s, l, t):
    '''
    address varchar(255) [unique, not null, note: 'to include unit number']
    '''
    init_dict = {
        'name': t['name'],
        'type_': t['type'],
    }
    # deprecated
    for constraint in t.get('constraints', []):
        if constraint == 'pk':
            init_dict['pk'] = True
        elif constraint == 'unique':
            init_dict['unique'] = True

    if 'settings' in t:
        init_dict.update(t['settings'])

    # comments after column definition have priority
    if 'comment' in t:
        init_dict['comment'] = t['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment

    return Column(**init_dict)


table_column.setParseAction(parse_column)
