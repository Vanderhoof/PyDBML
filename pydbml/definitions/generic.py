import pyparsing as pp

from pydbml.parser.blueprints import ExpressionBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

name = pp.Word(pp.unicode.alphanums + '_') | pp.QuotedString('"')
name_pattern = r'(\b\w+\b|\".*?\")'  # for use inside pp.Regex()

# Literals

string_literal = (
    pp.QuotedString("'", escChar="\\")
    ^ pp.QuotedString('"', escChar="\\")
    ^ pp.QuotedString("'''", escChar="\\", multiline=True)
)

expression_literal = pp.Regex(r"`[^`]*`").set_parse_action(lambda s, lok, tok: ExpressionBlueprint(tok[0]))

boolean_literal = (
    pp.CaselessLiteral('true')
    | pp.CaselessLiteral('false')
    | pp.CaselessLiteral('NULL')
)
number_literal = (
    pp.Word(pp.nums)
    ^ pp.Regex(r"\d+\.\d+")
)

# Expression

expr_chars = pp.Word(pp.alphanums + "\"'`,._+- \n\t")
expr_chars_no_comma_space = pp.Word(pp.alphanums + "\"'`._+-")
expression = pp.Forward()
factor = (
    pp.Word(pp.alphanums + '_')[0, 1] + '(' + expression + ')'
    | expr_chars_no_comma_space + (pp.Literal(",") | ");" | (pp.LineEnd() + ");"))
    | expr_chars
)
expression << factor[...]
