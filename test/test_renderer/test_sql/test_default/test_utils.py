from unittest.mock import Mock

from pydbml.classes import Enum
from pydbml.constants import ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY
from pydbml.renderer.sql.default.utils import (
    get_full_name_for_sql,
    reorder_tables_for_sql,
)


class TestGetFullNameForSQL:
    @staticmethod
    def test_public(enum1: Enum) -> None:
        assert get_full_name_for_sql(enum1) == '"product status"'

    @staticmethod
    def test_schema(enum1: Enum) -> None:
        enum1.schema = "myschema"
        assert get_full_name_for_sql(enum1) == '"myschema"."product status"'


def test_reorder_tables() -> None:
    t1 = Mock(name="table1")  # 1 ref
    t2 = Mock(name="table2")  # 2 refs
    t3 = Mock(name="table3")
    t4 = Mock(name="table4")  # 1 ref
    t5 = Mock(name="table5")
    t6 = Mock(name="table6")  # 3 refs
    t7 = Mock(name="table7")
    t8 = Mock(name="table8")
    t9 = Mock(name="table9")
    t10 = Mock(name="table10")

    refs = [
        Mock(type=ONE_TO_MANY, table1=t1, table2=t2, inline=True),
        Mock(type=MANY_TO_ONE, table1=t4, table2=t3, inline=True),
        Mock(type=ONE_TO_MANY, table1=t6, table2=t2, inline=True),
        Mock(type=ONE_TO_MANY, table1=t7, table2=t6, inline=True),
        Mock(type=MANY_TO_ONE, table1=t6, table2=t8, inline=True),
        Mock(type=ONE_TO_MANY, table1=t9, table2=t6, inline=True),
        Mock(
            type=ONE_TO_MANY, table1=t1, table2=t2, inline=False
        ),  # ignored not inline
        Mock(type=ONE_TO_MANY, table1=t10, table2=t1, inline=True),
        Mock(type=MANY_TO_MANY, table1=t1, table2=t2, inline=True),  # ignored m2m
    ]
    original = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10]
    expected = [t6, t2, t1, t4, t3, t5, t7, t8, t9, t10]
    result = reorder_tables_for_sql(original, refs)  # type: ignore
    assert expected == result
