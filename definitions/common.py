import pyparsing as pp
from .generic import string_literal

comment = "\\\\" + pp.SkipTo(pp.LineEnd() | pp.StringEnd())
note = pp.CaselessLiteral("note:") + string_literal
note_object = pp.CaselessLiteral('note') + '{' + string_literal + '}'
pk = pp.CaselessLiteral("pk")
unique = pp.CaselessLiteral("unique")
