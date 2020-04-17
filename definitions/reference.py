import pyparsing as pp
from definitions.generic import name
from definitions.common import __, _
from classes import Reference


relation = pp.oneOf("> - <")
ref_inline = pp.Literal("ref:") + relation('type') + name('table') + '.' + name('field')
ref_inline.setWhitespaceChars(' \t')


def parse_inline_relation(s, l, t):
    return Reference(type_=t['type'],
                     table2=t['table'],
                     col2=t['field'])


ref_inline.setParseAction(parse_inline_relation)


on_option = (
    pp.CaselessLiteral('no action') |
    pp.CaselessLiteral('restrict') |
    pp.CaselessLiteral('cascade') |
    pp.CaselessLiteral('set null') |
    pp.CaselessLiteral('set default')
)
update = pp.CaselessLiteral("update:").suppress() + _ + on_option
delete = pp.CaselessLiteral("delete:").suppress() + _ + on_option

ref_setting = _ + (update('update') | delete('delete')) + _

ref_settings = '[' + ref_setting + ']'


def parse_ref_settings(s, l, t):
    result = {}
    if 'update' in t:
        result['update'] = t['update'][0]
    if 'delete' in t:
        result['delete'] = t['delete'][0]
    return result


ref_settings.setParseAction(parse_ref_settings)

ref_body = (
    name('table1') +
    '.' +
    name('field1') +
    relation('type') +
    name('table2') +
    '.' +
    name('field2') +
    ref_settings('settings')[0, 1]
)

ref_short = pp.CaselessLiteral('ref') + name('name')[0, 1] + ':' + ref_body
ref_long = (
    pp.CaselessLiteral('ref') + __ +
    name('name')[0, 1] + _ +
    '{' + _ +
    ref_body + _ +
    '}'
)


def parse_ref(s, l, t):
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
    ref = Reference(**init_dict)
    return ref


ref_short.setParseAction(parse_ref)
ref_long.setParseAction(parse_ref)

ref = ref_short | ref_long
