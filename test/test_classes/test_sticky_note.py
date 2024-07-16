from pydbml._classes.sticky_note import StickyNote


def test_init_types():
    n1 = StickyNote('mynote', 'My note text')
    n2 = StickyNote('mynote', 3)
    n3 = StickyNote('mynote', [1, 2, 3])
    n4 = StickyNote('mynote', None)

    assert n1.text == 'My note text'
    assert n2.text == '3'
    assert n3.text == '[1, 2, 3]'
    assert n4.text == ''
    assert n1.name == n2.name == n3.name == n4.name == 'mynote'


def test_str(sticky_note1: StickyNote) -> None:
    assert str(sticky_note1) == "StickyNote('mynote', 'Simple note')"


def test_repr(sticky_note1: StickyNote) -> None:
    assert repr(sticky_note1) == "<StickyNote 'mynote', 'Simple note'>"


def test_bool(sticky_note1: StickyNote) -> None:
    assert bool(sticky_note1) is True
    sticky_note1.text = ''
    assert bool(sticky_note1) is False
