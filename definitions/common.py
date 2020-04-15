import pyparsing as pp
from .generic import string_literal
from classes import Note

comment = pp.Suppress("//") + pp.SkipTo(pp.LineEnd() | pp.StringEnd())


note = pp.CaselessLiteral("note:") + string_literal('text')
note.addParseAction(lambda s, l, t: Note(t[1]))

note_object = pp.CaselessLiteral('note') + '{' + string_literal + '}'
pk = pp.CaselessLiteral("pk")
unique = pp.CaselessLiteral("unique")
