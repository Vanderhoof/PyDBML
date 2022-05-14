from unittest import TestCase

from pydbml.classes import Expression
from pydbml.parser.blueprints import ExpressionBlueprint


class TestNote(TestCase):
    def test_build(self) -> None:
        bp = ExpressionBlueprint(text='amount*2')
        result = bp.build()
        self.assertIsInstance(result, Expression)
        self.assertEqual(result.text, bp.text)
