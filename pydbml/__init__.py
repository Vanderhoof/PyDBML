import doctest
import unittest

from . import classes
from pydbml.parser import PyDBML
from pydbml.parser.blueprints import MANY_TO_ONE
from pydbml.parser.blueprints import ONE_TO_MANY
from pydbml.parser.blueprints import ONE_TO_ONE


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(classes))
    return tests
