from pydbml.classes import Column
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Table


def test_note_property():
    note1 = Note('column note')
    t = Table('products')
    c = Column('id', 'integer')
    i = Index(subjects=[c])
    i.note = note1
    assert i.note.parent is i


def test_repr(index1: Index) -> None:
    assert repr(index1) == "<Index 'products', ['name']>"


def test_str(index1: Index) -> None:
    assert str(index1) == 'Index(products[name])'
