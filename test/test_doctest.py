import doctest

from pydbml import database
from pydbml.classes import column
from pydbml.classes import enum
from pydbml.classes import expression
from pydbml.classes import index
from pydbml.classes import note
from pydbml.classes import project
from pydbml.classes import reference
from pydbml.classes import table
from pydbml.classes import table_group
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
