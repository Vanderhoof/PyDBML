import pyparsing as pp

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
from pydbml.parser.blueprints import ColumnBlueprint


pp.ParserElement.set_default_whitespace_chars(' \t\r')

type_args = ("(" + pp.original_text_for(expression) + ")")

# column type is parsed as a single string, it will be split by blueprint
column_type = pp.Combine((name + '.' + name) | ((name) + type_args[0, 1]))

default = pp.CaselessLiteral('default:').suppress() + _ - (
    string_literal
    | expression_literal
    | boolean_literal.set_parse_action(
        lambda s, loc, tok: {
            'true': True,
            'false': False,
            'NULL': None
        }[tok[0]]
    )
    | number_literal.set_parse_action(
        lambda s, loc, tok: float(''.join(tok[0])) if '.' in tok[0] else int(tok[0])
    )
)


column_setting = _ + (
    pp.CaselessLiteral("not null").set_parse_action(
        lambda s, loc, tok: True
    )('notnull')
    | pp.CaselessLiteral("null").set_parse_action(
        lambda s, loc, tok: False
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


def parse_column_settings(s, loc, tok):
    '''
    [ NOT NULL, increment, default: `now()`]
    '''
    result = {}
    if tok.get('notnull'):
        result['not_null'] = True
    if 'pk' in tok:
        result['pk'] = True
    if 'unique' in tok:
        result['unique'] = True
    if 'increment' in tok:
        result['autoinc'] = True
    if 'note' in tok:
        result['note'] = tok['note']
    if 'default' in tok:
        result['default'] = tok['default'][0]
    if 'ref' in tok:
        result['ref_blueprints'] = list(tok['ref'])
    if 'comment' in tok:
        result['comment'] = tok['comment'][0]
    return result


column_settings.set_parse_action(parse_column_settings)


constraint = pp.CaselessLiteral("unique") | pp.CaselessLiteral("pk")

table_column = _c + (
    name('name')
    + column_type('type')
    + constraint[...]('constraints') + c
    + column_settings('settings')[0, 1]
) + n


def parse_column(s, loc, tok):
    '''
    address varchar(255) [unique, not null, note: 'to include unit number']
    '''
    init_dict = {
        'name': tok['name'],
        'type': tok['type'],
    }
    # deprecated
    for constraint in tok.get('constraints', []):
        if constraint == 'pk':
            init_dict['pk'] = True
        elif constraint == 'unique':
            init_dict['unique'] = True

    if 'settings' in tok:
        init_dict.update(tok['settings'])

    # comments after column definition have priority
    if 'comment' in tok:
        init_dict['comment'] = tok['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment

    return ColumnBlueprint(**init_dict)


table_column.set_parse_action(parse_column)
