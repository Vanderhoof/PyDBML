import pyparsing as pp
from pydbml.definitions.generic import expression_literal, name, string_literal
from pydbml.definitions.common import _, _c, c, pk, unique, note
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
    '[' + pk('pk') + ']' + c |
    '[' + index_setting + (',' + index_setting)[...] + ']' + c
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
    if 'comment' in t:
        result['comment'] = t['comment'][0]
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
)('subject') + c + index_settings('settings')[0, 1]

single_index_syntax = single_index('subject') + c + index_settings('settings')[0, 1]
index = _c + (single_index_syntax ^ composite_index_syntax)


def parse_index(s, l, t):
    init_dict = {}
    if isinstance(t['subject'], str):
        subjects = [t['subject']]
    else:
        subjects = list(t['subject'])

    init_dict['subjects'] = subjects
    settings = t.get('settings', {})
    init_dict.update(settings)

    # comments after settings have priority
    if 'comment' in t:
        init_dict['comment'] = t['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment
    return Index(**init_dict)


index.setParseAction(parse_index)
