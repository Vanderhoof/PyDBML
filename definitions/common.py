import pyparsing as pp
from .generic import string_literal
from classes import Note

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

comment = pp.Suppress("//") + pp.SkipTo(pp.LineEnd() | pp.StringEnd())

# optional comment or newline
_ = ('\n' | comment)[...].suppress()

# obligatory any whitespace
__ = (pp.White() | comment)[1, ...].suppress()

# optional comment and obligatory newline
n = (comment[0, 1] + '\n')[...].suppress()

note = pp.CaselessLiteral("note:") + _ + string_literal('text')
note.setParseAction(lambda s, l, t: Note(t['text'][0]))

note_object = pp.CaselessLiteral('note') + _ + '{' + _ + string_literal('text') + _ + '}'
note_object.setParseAction(lambda s, l, t: Note(t['text'][0]))

pk = pp.CaselessLiteral("pk")
unique = pp.CaselessLiteral("unique")
