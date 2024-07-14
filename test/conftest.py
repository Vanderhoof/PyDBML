from textwrap import dedent

import pytest

from pydbml import Database
from pydbml._classes.reference import Reference
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
def simple_column_with_table(db: Database, table1: Table, simple_column: Column) -> Column:
    table1.add_column(simple_column)
    db.add(table1)
    return simple_column


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
def complex_column_with_table(db: Database, table1: Table, complex_column: Column) -> Column:
    table1.add_column(complex_column)
    db.add(table1)
    return complex_column


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
def table2() -> Table:
    return Table(
        name='products',
        columns=[
            Column('id', 'integer'),
            Column('name', 'varchar'),
        ]
    )


@pytest.fixture
def table3() -> Table:
    return Table(
        name='orders',
        columns=[
            Column('id', 'integer'),
            Column('product_id', 'integer'),
            Column('price', 'float'),
        ]
    )

@pytest.fixture
def reference1(table2: Table, table3: Table) -> Reference:
    return Reference(
        type='>',
        col1=[table3.columns[1]],
        col2=[table2.columns[0]],
    )


@pytest.fixture
def index1(table1: Table) -> Index:
    result = Index(
        subjects=[table1.columns[1]]
    )
    table1.add_index(result)
    return result


@pytest.fixture
def note1():
    return Note('Simple note')


@pytest.fixture
def multiline_note():
    return Note(
        dedent(
            '''\
            This is a multiline note.
            It has multiple lines.'''
        )
    )
