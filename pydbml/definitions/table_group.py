import pyparsing as pp

from .common import _, note, note_object
from .common import _c
from .common import end
from .generic import name
from pydbml.parser.blueprints import TableGroupBlueprint, NoteBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

table_name = pp.Combine(name + '.' + name) | name
note_element = note | note_object

tg_element = _ + (note_element('note') | table_name.set_results_name('items', list_all_matches=True)) + _

tg_body = tg_element[...]

tg_settings = '[' + _ + note('note') + _ + ']'



table_group = _c + (
    pp.CaselessLiteral('TableGroup')
    - name('name') + _
    + tg_settings[0, 1] + _
    - '{' + _
    - tg_body + _
    - '}'
) + end


def parse_table_group(s, loc, tok):
    '''
    TableGroup tablegroup_name {
        table1
        table2
        table3
    }
    '''
    init_dict = {
        'name': tok['name'],
        'items': list(tok.get('items', []))
    }
    if 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment
    if 'note' in tok:
        note = tok['note']
        init_dict['note'] = note if isinstance(note, NoteBlueprint) else note[0]
    return TableGroupBlueprint(**init_dict)


table_group.set_parse_action(parse_table_group)
