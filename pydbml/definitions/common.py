import pyparsing as pp

from .generic import string_literal
from pydbml.parser.blueprints import NoteBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

comment = (
    pp.Suppress("//") + pp.SkipTo(pp.LineEnd())
    | pp.Suppress('/*') + ... + pp.Suppress('*/')
)

# optional comment or newline
_ = ('\n' | comment)[...].suppress()

# optional comment or newline, but comments are captured
_c = (pp.Suppress('\n') | comment('comment_before*'))[...]

# optional captured comment
c = comment('comment')[0, 1]

n = pp.LineEnd()
end = n | pp.StringEnd()
# obligatory newline
# n = pp.Suppress('\n')[1, ...]

note = pp.CaselessLiteral("note:") + _ - string_literal('text')
note.set_parse_action(lambda s, loc, tok: NoteBlueprint(tok['text']))

note_object = pp.CaselessLiteral('note') + _ - '{' + _ - string_literal('text') + _ - '}'
note_object.set_parse_action(lambda s, loc, tok: NoteBlueprint(tok['text']))

pk = pp.CaselessLiteral("pk")
unique = pp.CaselessLiteral("unique")
