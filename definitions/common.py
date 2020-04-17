import pyparsing as pp
from .generic import string_literal
from classes import Note

comment = pp.Suppress("//") + pp.SkipTo(pp.LineEnd() | pp.StringEnd())

# optional comment or newline
_ = ('\n' | comment)[...].suppress()

# obligatory any whitespace
__ = (pp.White() | comment)[1, ...].suppress()

# optional comment and obligatory newline
n = (comment[0, 1] + '\n')[...].suppress()

note = pp.CaselessLiteral("note:") + _ + string_literal('text')
note.setParseAction(lambda s, l, t: Note(t[1]))

note_object = pp.CaselessLiteral('note') + _ + '{' + _ + string_literal + _ + '}'
pk = pp.CaselessLiteral("pk")
unique = pp.CaselessLiteral("unique")
