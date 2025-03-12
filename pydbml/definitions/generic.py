import pyparsing as pp

from pydbml.parser.blueprints import ExpressionBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

name = pp.Word(pp.alphanums + '_') | pp.QuotedString('"')

# Literals

string_literal = (
    pp.QuotedString("'", escChar="\\")
    ^ pp.QuotedString('"', escChar="\\")
    ^ pp.QuotedString("'''", escChar="\\", multiline=True)
)
expression_literal = pp.Combine(
    pp.Suppress('`')
    + pp.CharsNotIn('`')[...]
    + pp.Suppress('`')
).set_parse_action(lambda s, lok, tok: ExpressionBlueprint(tok[0]))

boolean_literal = (
    pp.CaselessLiteral('true')
    | pp.CaselessLiteral('false')
    | pp.CaselessLiteral('NULL')
)
number_literal = (
    pp.Word(pp.nums)
    ^ pp.Combine(
        pp.Word(pp.nums) + '.' + pp.Word(pp.nums)
    )
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
