import pyparsing as pp

from pydbml.classes import Note

from .generic import string_literal

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

comment = pp.Suppress("//") + pp.SkipTo(pp.LineEnd())

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
note.setParseAction(lambda s, l, t: Note(t['text']))

note_object = pp.CaselessLiteral('note') + _ - '{' + _ - string_literal('text') + _ - '}'
note_object.setParseAction(lambda s, l, t: Note(t['text']))

pk = pp.CaselessLiteral("pk")
unique = pp.CaselessLiteral("unique")
