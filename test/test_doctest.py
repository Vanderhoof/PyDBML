import doctest

from pydbml import database
from pydbml._classes import column
from pydbml._classes import enum
from pydbml._classes import expression
from pydbml._classes import index
from pydbml._classes import note
from pydbml._classes import project
from pydbml._classes import reference
from pydbml._classes import table
from pydbml._classes import table_group
from pydbml.parser import parser


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(column))
    tests.addTests(doctest.DocTestSuite(enum))
    tests.addTests(doctest.DocTestSuite(expression))
    tests.addTests(doctest.DocTestSuite(index))
    tests.addTests(doctest.DocTestSuite(project))
    tests.addTests(doctest.DocTestSuite(note))
    tests.addTests(doctest.DocTestSuite(reference))
    tests.addTests(doctest.DocTestSuite(database))
    tests.addTests(doctest.DocTestSuite(table))
    tests.addTests(doctest.DocTestSuite(table_group))
    tests.addTests(doctest.DocTestSuite(parser))
    return tests
