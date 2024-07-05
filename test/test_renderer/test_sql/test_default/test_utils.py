from pydbml.classes import Enum
from pydbml.renderer.sql.default.utils import get_full_name_for_sql


class TestGetFullNameForSQL:
    @staticmethod
    def test_public(enum1: Enum) -> None:
        assert get_full_name_for_sql(enum1) == '"product status"'

    @staticmethod
    def test_schema(enum1: Enum) -> None:
        enum1.schema = 'myschema'
        assert get_full_name_for_sql(enum1) == '"myschema"."product status"'
