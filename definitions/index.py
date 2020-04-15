import pyparsing as pp
from definitions.generic import expression_literal, name, string_literal
from definitions.common import pk, unique, comment
from classes import Index

table_type = pp.CaselessLiteral("type:") + (
    pp.CaselessLiteral("btree") | pp.CaselessLiteral("hash")
)
index_setting = (
    unique('unique') |
    table_type('type') |
    pp.CaselessLiteral("name:") + string_literal('name')
)
index_settings = (
    '[' + pk('pk') + ']' |
    '[' + index_setting + (',' + index_setting)[...] + ']'
)


def parse_index_settings(s, l, t):
    result = {}
    if 'unique' in t:
        result['unique'] = True
    if 'name' in t:
        result['name'] = t['name']
    if 'pk' in t:
        result['pk'] = True
    if 'type' in t:
        result['type_'] = t['type']
    return result


index_settings.setParseAction(parse_index_settings)

single_index = name | expression_literal
composite_index_syntax = (
    pp.Suppress('(') +
    single_index + (
        pp.Suppress(',') +
        single_index
    )[...] +
    pp.Suppress(')')
)('subject') + index_settings('settings')[0, 1]

single_index_syntax = single_index('subject') + index_settings('settings')[0, 1]
index = single_index_syntax ^ composite_index_syntax


def parse_index(s, l, t):
    if isinstance(t['subject'], str):
        subjects = [t['subject']]
    else:
        subjects = list(t['subject'])
    settings = t.get('settings', {})
    return Index(subjects=subjects, **settings)


index.setParseAction(parse_index)
index.ignore(comment)
