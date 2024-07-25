from pydbml.classes import Note


def test_init_types():
    n1 = Note('My note text')
    n2 = Note(3)
    n3 = Note([1, 2, 3])
    n4 = Note(None)
    n5 = Note(n1)

    assert n1.text == 'My note text'
    assert n2.text == '3'
    assert n3.text == '[1, 2, 3]'
    assert n4.text == ''
    assert n5.text == 'My note text'


def test_str(note1: Note) -> None:
    assert str(note1) == 'Simple note'


def test_repr(note1: Note) -> None:
    assert repr(note1) == "Note('Simple note')"
