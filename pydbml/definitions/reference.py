import pyparsing as pp

from .common import _
from .common import _c
from .common import c
from .common import n
from .generic import name
from pydbml.parser.blueprints import ReferenceBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

relation = pp.oneOf("> - < <>")

col_name = (
    (
        name('schema') + '.' + name('table') + '.' - name('field')
    ) | (
        name('table') + '.' + name('field')
    )
)

ref_inline = pp.Literal("ref:") - relation('type') - col_name


def parse_inline_relation(s, loc, tok):
    '''
    ref: < table.column
    or
    ref: < schema1.table.column
    '''
    result = {
        'type': tok['type'],
        'inline': True,
        'table2': tok['table'],
        'col2': tok['field']
    }
    if 'schema' in tok:
        result['schema2'] = tok['schema']
    return ReferenceBlueprint(**result)


ref_inline.set_parse_action(parse_inline_relation)

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


def parse_ref_settings(s, loc, tok):
    '''
    [delete: cascade]
    '''
    result = {}
    if 'update' in tok:
        result['on_update'] = tok['update'][0]
    if 'delete' in tok:
        result['on_delete'] = tok['delete'][0]
    if 'comment' in tok:
        result['comment'] = tok['comment'][0]
    return result


ref_settings.set_parse_action(parse_ref_settings)

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


def parse_ref_cols(s, loc, tok):
    '''
    table1.col1
    or
    schema1.table1.col1
    or
    schema1.table1.(col1, col2)
    '''
    result = {
        'table': tok['table'],
        'field': tok['field'],
    }
    if 'schema' in tok:
        result['schema'] = tok['schema']
    return result


ref_cols.set_parse_action(parse_ref_cols)

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


def parse_ref(s, loc, tok):
    '''
    ref name: table1.col1 > table2.col2
    or
    ref name {
        table1.col1 < table2.col2
    }
    '''
    init_dict = {
        'type': tok['type'],
        'inline': False,
        'table1': tok['col1']['table'],
        'col1': tok['col1']['field'],
        'table2': tok['col2']['table'],
        'col2': tok['col2']['field'],
    }

    if 'schema' in tok['col1']:
        init_dict['schema1'] = tok['col1']['schema']
    if 'schema' in tok['col2']:
        init_dict['schema2'] = tok['col2']['schema']
    if 'name' in tok:
        init_dict['name'] = tok['name']
    if 'settings' in tok:
        init_dict.update(tok['settings'])

    # comments after settings have priority
    if 'comment' in tok:
        init_dict['comment'] = tok['comment'][0]
    if 'comment' not in init_dict and 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment

    ref = ReferenceBlueprint(**init_dict)
    return ref


ref_short.set_parse_action(parse_ref)
ref_long.set_parse_action(parse_ref)

ref = ref_short | ref_long + (n | pp.StringEnd())
