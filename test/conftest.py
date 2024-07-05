
import pytest

from pydbml import Database
from pydbml.classes import Column, Enum, EnumItem, Note, Expression, Table, Index


@pytest.fixture
def db():
    return Database()


@pytest.fixture
def enum_item1():
    return EnumItem('en-US')


@pytest.fixture
def enum1():
    return Enum('product status', ('production', 'development'))


@pytest.fixture
def expression1() -> Expression:
    return Expression('SUM(amount)')


@pytest.fixture
def simple_column() -> Column:
    return Column(
        name='id',
        type='integer'
    )


@pytest.fixture
def complex_column(enum1: Enum) -> Column:
    return Column(
        name='counter',
        type=enum1,
        pk=True,
        autoinc=True,
        unique=True,
        not_null=True,
        default=0,
        comment='This is a counter column',
        note=Note('This is a note for the column')
    )


@pytest.fixture
def table1() -> Table:
    return Table(
        name='products',
        columns=[
            Column('id', 'integer'),
            Column('name', 'varchar'),
        ]
    )


@pytest.fixture
def index1(table1: Table) -> Index:
    result = Index(
        subjects=[table1.columns[1]]
    )
    table1.add_index(result)
    return result
