import pyparsing as pp
from pydbml.definitions.generic import (expression, name, string_literal, boolean_literal,
                                        number_literal, expression_literal)
from pydbml.definitions.common import _, n, note, pk, unique
from pydbml.definitions.reference import ref_inline
from pydbml.classes import Column


pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

type_args = ("(" + pp.originalTextFor(expression)('args') + ")")
type_name = (pp.Word(pp.alphanums + '_[]') | pp.dblQuotedString())('name')
column_type = (type_name + type_args[0, 1])


def parse_column_type(s, l, t):
    result = t['name']
    args = t.get('args')
    result += '(' + args + ')' if args else ''
    return result


column_type.setParseAction(parse_column_type)


default = pp.CaselessLiteral('default:').suppress() + _ + (
    string_literal |
    expression_literal |
    boolean_literal.setParseAction(
        lambda s, l, t: {
            'true': True,
            'false': False,
            'null': None
        }[t[0]]
    ) |
    number_literal.setParseAction(
        lambda s, l, t: float(''.join(t[0])) if '.' in t[0] else int(t[0])
    )
)


column_setting = _ + (
    pp.CaselessLiteral("not null")('nn') |
    pp.CaselessLiteral("null")('n') |
    pp.CaselessLiteral("primary key")('pk') |
    pk('pk') |
    unique('u') |
    pp.CaselessLiteral("increment")('i') |
    note('n') |
    ref_inline('r*') |
    default('d') + _
)
column_settings = '[' + column_setting + ("," + column_setting)[...] + ']' + n


def parse_column_settings(s, l, t):
    result = {}
    if 'nn' in t:
        result['not_null'] = True
    if 'pk' in t:
        result['pk'] = True
    if 'u' in t:
        result['unique'] = True
    if 'i' in t:
        result['autoinc'] = True
    if 'n' in t:
        result['note'] = t['n']
    if 'd' in t:
        result['default'] = t['d'][0]
    if 'r' in t:
        result['refs'] = list(t['r'])
    return result


column_settings.setParseAction(parse_column_settings)


constraint = pp.CaselessLiteral("unique") | pp.CaselessLiteral("pk")

table_column = _ + (
    name('name') +
    column_type('type') +
    constraint('constraints')[...] +
    column_settings('settings')[0, 1]
) + n


def parse_column(s, l, t):
    # TODO add validation and ref processing
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

    return Column(**init_dict)


table_column.setParseAction(parse_column)
