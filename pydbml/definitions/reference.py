import pyparsing as pp

from pydbml.parser.blueprints import ReferenceBlueprint

from .common import _
from .common import _c
from .common import c
from .common import n
from .generic import name

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

relation = pp.oneOf("> - <")

col_name = (
    (
        name('schema') + '.' + name('table') + '.' - name('field')
    ) | (
        name('table') + '.' + name('field')
    )
)

ref_inline = pp.Literal("ref:") - relation('type') - col_name


def parse_inline_relation(s, l, t):
    '''
    ref: < table.column
    or
    ref: < schema1.table.column
    '''
    result = {
        'type': t['type'],
        'inline': True,
        'table2': t['table'],
        'col2': t['field']
    }
    if 'schema' in t:
        result['schema2'] = t['schema']
    return ReferenceBlueprint(**result)


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

ref_cols = (
    (
        name('schema')
        + pp.Suppress('.') + name('table')
        + pp.Suppress('.') + name_or_composite('field')
    ) | (
        name('table')
        + pp.Suppress('.') + name_or_composite('field')
    )
)


def parse_ref_cols(s, l, t):
    '''
    table1.col1
    or
    schema1.table1.col1
    or
    schema1.table1.(col1, col2)
    '''
    result = {
        'table': t['table'],
        'field': t['field'],
    }
    if 'schema' in t:
        result['schema'] = t['schema']
    return result


ref_cols.setParseAction(parse_ref_cols)

ref_body = (
    ref_cols('col1')
    - relation('type')
    - ref_cols('col2') + c
    + ref_settings('settings')[0, 1]
)
# ref_body = (
#     table_name('table1')
#     - '.'
#     - name_or_composite('field1')
#     - relation('type')
#     - table_name('table2')
#     - '.'
#     - name_or_composite('field2') + c
#     + ref_settings('settings')[0, 1]
# )


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
        'type': t['type'],
        'inline': False,
        'table1': t['col1']['table'],
        'col1': t['col1']['field'],
        'table2': t['col2']['table'],
        'col2': t['col2']['field'],
    }

    if 'schema' in t['col1']:
        init_dict['schema1'] = t['col1']['schema']
    if 'schema' in t['col2']:
        init_dict['schema2'] = t['col2']['schema']
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
