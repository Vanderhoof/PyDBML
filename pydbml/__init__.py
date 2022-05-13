import doctest
import unittest

from . import classes
from .parser import PyDBML

from pydbml.constants import MANY_TO_ONE
from pydbml.constants import ONE_TO_MANY
from pydbml.constants import ONE_TO_ONE


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(classes))
    return tests
