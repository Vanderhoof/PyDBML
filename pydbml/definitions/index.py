import pyparsing as pp
from pydbml.definitions.generic import expression_literal, name, string_literal
from pydbml.definitions.common import _, pk, unique, note
from pydbml.classes import Index

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

table_type = pp.CaselessLiteral("type:") + (
    pp.CaselessLiteral("btree") | pp.CaselessLiteral("hash")
)
index_setting = (
    unique('unique') |
    table_type('type') |
    pp.CaselessLiteral("name:") + string_literal('name') |
    note('note')
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
    if 'note' in t:
        result['note'] = t['note']
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
index = _ + (single_index_syntax ^ composite_index_syntax) + _


def parse_index(s, l, t):
    if isinstance(t['subject'], str):
        subjects = [t['subject']]
    else:
        subjects = list(t['subject'])
    settings = t.get('settings', {})
    return Index(subjects=subjects, **settings)


index.setParseAction(parse_index)
