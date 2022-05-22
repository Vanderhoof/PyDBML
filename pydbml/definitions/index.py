import pyparsing as pp

from .common import _
from .common import _c
from .common import c
from .common import note
from .common import pk
from .common import unique
from .generic import expression_literal
from .generic import name
from .generic import string_literal
from pydbml.parser.blueprints import ExpressionBlueprint
from pydbml.parser.blueprints import IndexBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

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


def parse_index_settings(s, lok, tok):
    '''
    [type: btree, name: 'name', unique, note: 'note']
    '''
    result = {}
    if 'unique' in tok:
        result['unique'] = True
    if 'name' in tok:
        result['name'] = tok['name']
    if 'pk' in tok:
        result['pk'] = True
    if 'type' in tok:
        result['type'] = tok['type']
    if 'note' in tok:
        result['note'] = tok['note']
    if 'comment' in tok:
        result['comment'] = tok['comment'][0]
    return result


index_settings.set_parse_action(parse_index_settings)

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


def parse_index(s, lok, tok):
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
    if isinstance(tok['subject'], (str, ExpressionBlueprint)):
        subjects = [tok['subject']]
    else:
        subjects = list(tok['subject'])

    init_dict['subject_names'] = subjects
    settings = tok.get('settings', {})
    init_dict.update(settings)

    # comments after settings have priority
    if 'comment' in tok:
        init_dict['comment'] = tok['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment
    return IndexBlueprint(**init_dict)


index.set_parse_action(parse_index)
