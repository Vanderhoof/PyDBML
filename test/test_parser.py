import os

from pathlib import Path
from unittest import TestCase

from pydbml.parser.blueprints import EnumItemBlueprint
from pydbml.parser.blueprints import EnumBlueprint
from pydbml import PyDBMLParser
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import TableNotFoundError


TEST_DATA_PATH = Path(os.path.abspath(__file__)).parent / 'test_data'


class TestParser(TestCase):
    def test_build_enums(self) -> None:
        i1 = EnumItemBlueprint()