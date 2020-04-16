import pyparsing as pp
from definitions.generic import (expression, name, string_literal, boolean_literal,
                                 number_literal)
from definitions.common import note, comment, pk, unique
from definitions.reference import ref_inline
from classes import ColumnType, Column, ReferenceRegistry


def parse_column_type(s, l, t):
    return ColumnType(name=t['name'],
                      args=t.get('args'))


type_args = ("(" + pp.originalTextFor(expression)('args') + ")")
type_name = (pp.Word(pp.alphanums + '_[]') | pp.dblQuotedString())('name')
column_type = (type_name + type_args[0, 1])
column_type.setParseAction(parse_column_type)


default = pp.CaselessLiteral('default:') + (
    string_literal |
    expression |
    boolean_literal.setParseAction(
        lambda s, l, t: {
            'true': True,
            'false': False,
            'null': None
        }[t[0]]
    ) |
    number_literal.setParseAction(
        lambda s, l, t: float(''.join(t)) if len(t) > 1 else int(t)
    )
)


column_setting = (
    pp.CaselessLiteral("not null")('nn') |
    pp.CaselessLiteral("null")('n') |
    pp.CaselessLiteral("primary key")('pk') |
    pk('pk') |
    unique('u') |
    pp.CaselessLiteral("increment")('i') |
    note('n') |
    ref_inline('r') |
    default('d')
)
column_settings = '[' + column_setting + ("," + column_setting)[...] + ']'


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
        result['default'] = t['d']
    if 'r' in t:
        result['ref'] = t['r']
    return result


column_settings.setParseAction(parse_column_settings)


constraint = pp.CaselessLiteral("unique") | pp.CaselessLiteral("pk")

table_column = (
    name('name') +
    column_type('type') +
    constraint('constraints')[...] +
    column_settings('settings')[0, 1]
)


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
table_column.ignore(comment)
