import pyparsing as pp

from pydbml.classes import ReferenceBlueprint

from .common import _
from .common import _c
from .common import c
from .common import n
from .generic import name

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

relation = pp.oneOf("> - <")
ref_inline = pp.Literal("ref:") - relation('type') - name('table') - '.' - name('field')


def parse_inline_relation(s, l, t):
    '''
    ref: < table.column
    '''
    return ReferenceBlueprint(type_=t['type'],
                              table2=t['table'],
                              col2=t['field'])


ref_inline.setParseAction(parse_inline_relation)

on_option = (
    pp.CaselessLiteral('no action')
    | pp.CaselessLiteral('restrict')
    | pp.CaselessLiteral('cascade')
    | pp.CaselessLiteral('set null')
    | pp.CaselessLiteral('set default')
)
update = pp.CaselessLiteral("update:").suppress() + _ + on_option
delete = pp.CaselessLiteral("delete:").suppress() + _ + on_option

ref_setting = _ + (update('update') | delete('delete')) + _

ref_settings = (
    '['
    + ref_setting
    + (
        ','
        + ref_setting
    )[...]
    + ']' + c
)


def parse_ref_settings(s, l, t):
    '''
    [delete: cascade]
    '''
    result = {}
    if 'update' in t:
        result['on_update'] = t['update'][0]
    if 'delete' in t:
        result['on_delete'] = t['delete'][0]
    if 'comment' in t:
        result['comment'] = t['comment'][0]
    return result


ref_settings.setParseAction(parse_ref_settings)

composite_name = (
    '(' + pp.White()[...]
    - name + pp.White()[...]
    + (
        pp.White()[...] + ","
        + pp.White()[...] + name
        + pp.White()[...]
    )[...]
    + ')'
)
name_or_composite = name | pp.Combine(composite_name)

ref_body = (
    name('table1')
    - '.'
    - name_or_composite('field1')
    - relation('type')
    - name('table2')
    - '.'
    - name_or_composite('field2') + c
    + ref_settings('settings')[0, 1]
)


ref_short = _c + pp.CaselessLiteral('ref') + name('name')[0, 1] + ':' - ref_body
ref_long = _c + (
    pp.CaselessLiteral('ref') + _
    + name('name')[0, 1] + _
    + '{' + _
    - ref_body + _
    - '}'
)


def parse_ref(s, l, t):
    '''
    ref name: table1.col1 > table2.col2
    or
    ref name {
        table1.col1 < table2.col2
    }
    '''
    init_dict = {
        'type_': t['type'],
        'table1': t['table1'],
        'col1': t['field1'],
        'table2': t['table2'],
        'col2': t['field2']
    }
    if 'name' in t:
        init_dict['name'] = t['name']
    if 'settings' in t:
        init_dict.update(t['settings'])

    # comments after settings have priority
    if 'comment' in t:
        init_dict['comment'] = t['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment

    ref = ReferenceBlueprint(**init_dict)
    return ref


ref_short.setParseAction(parse_ref)
ref_long.setParseAction(parse_ref)

ref = ref_short | ref_long + (n | pp.StringEnd())
