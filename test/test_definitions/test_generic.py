from unittest import TestCase

from pyparsing import ParserElement

from pydbml.definitions.generic import expression_literal
from pydbml.parser.blueprints import ExpressionBlueprint


ParserElement.setDefaultWhitespaceChars(' \t\r')


class TestExpressionLiteral(TestCase):
    def test_expression_literal(self) -> None:
        val = '`SUM(amount)`'
        res = expression_literal.parseString(val)
        self.assertIsInstance(res[0], ExpressionBlueprint)
        self.assertEqual(res[0].text, 'SUM(amount)')
