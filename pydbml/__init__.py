from pydbml.parser import PyDBML, PyDBMLParseResults
import unittest
import doctest
from . import classes


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(classes))
    return tests