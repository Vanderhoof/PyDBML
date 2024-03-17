import pyparsing as pp

from .common import _, end, _c
from .generic import string_literal, name
from ..parser.blueprints import StickyNoteBlueprint

sticky_note = _c + pp.CaselessLiteral('note') + _ + (name('name') + _ - '{' + _ - string_literal('text') + _ - '}') + end


def parse_sticky_note(s, loc, tok):
    '''
    Note single_line_note {
      'This is a single line note'
    }
    '''
    init_dict = {'name': tok['name'], 'text': tok['text']}

    return StickyNoteBlueprint(**init_dict)


sticky_note.set_parse_action(parse_sticky_note)
