import pyparsing as pp

from pydbml.classes import Index

from .common import _
from .common import _c
from .common import c
from .common import note
from .common import pk
from .common import unique
from .generic import expression_literal
from .generic import name
from .generic import string_literal

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

index_type = pp.CaselessLiteral("type:").suppress() + _ - (
    pp.CaselessLiteral("btree")('type') | pp.CaselessLiteral("hash")('type')
)
index_setting = (
    unique('unique')
    | index_type
    | pp.CaselessLiteral("name:") + _ - string_literal('name')
    | note('note')
)
index_settings = (
    '[' + _ + pk('pk') + _ - ']' + c
    | '[' + _ + index_setting + (_ + ',' + _ - index_setting)[...] + _ - ']' + c
)


def parse_index_settings(s, l, t):
    '''
    [type: btree, name: 'name', unique, note: 'note']
    '''
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

subject = name | expression_literal
composite_index_syntax = (
    pp.Suppress('(')
    + subject + (
        pp.Suppress(',')
        + subject
    )[...]
    + pp.Suppress(')')
)('subject') + c + index_settings('settings')[0, 1]

single_index_syntax = subject('subject') + c + index_settings('settings')[0, 1]
index = _c + (single_index_syntax ^ composite_index_syntax) + c

indexes = (
    pp.CaselessLiteral('indexes').suppress() + _
    - pp.Suppress('{')
    - index[1, ...] + _
    + pp.Suppress('}')
)


def parse_index(s, l, t):
    '''
        (id, country) [pk] // composite primary key
        or
        "created_at"
        or
        booking_date [
          name: 'name',
          unique
        ]
    '''
    init_dict = {}
    if isinstance(t['subject'], str):
        subjects = [t['subject']]
    else:
        subjects = list(t['subject'])

    init_dict['subject_names'] = subjects
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
