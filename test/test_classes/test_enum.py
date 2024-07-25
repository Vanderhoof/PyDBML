from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Note
from unittest import TestCase


class TestEnumItem(TestCase):
    def test_note_property(self):
        note1 = Note('enum item note')
        ei = EnumItem('en-US', note='preferred', comment='EnumItem comment')
        ei.note = note1
        self.assertIs(ei.note.parent, ei)


class TestEnum(TestCase):
    def test_getitem(self) -> None:
        ei = EnumItem('created')
        items = [
            EnumItem('running'),
            ei,
            EnumItem('donef'),
            EnumItem('failure'),
        ]
        e = Enum('job_status', items)
        self.assertIs(e[1], ei)
        with self.assertRaises(IndexError):
            e[22]
        with self.assertRaises(TypeError):
            e['abc']

    def test_iter(self) -> None:
        ei1 = EnumItem('created')
        ei2 = EnumItem('running')
        ei3 = EnumItem('donef')
        ei4 = EnumItem('failure')
        items = [
            ei1,
            ei2,
            ei3,
            ei4,
        ]
        e = Enum('job_status', items)

        for i1, i2 in zip(e, [ei1, ei2, ei3, ei4]):
            self.assertIs(i1, i2)


def test_repr(enum_item1: EnumItem) -> None:
    assert repr(enum_item1) == "<EnumItem 'en-US'>"


def test_str() -> None:
    ei = EnumItem('en-US')
    assert str(ei) == 'en-US'
