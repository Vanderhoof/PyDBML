from pydbml.classes import Note
from pydbml.classes import Project


def test_note_property():
    note1 = Note('column note')
    p = Project('myproject')
    p.note = note1
    assert p.note.parent is p


def test_repr() -> None:
    project = Project('myproject')
    assert repr(project) == "<Project 'myproject'>"

