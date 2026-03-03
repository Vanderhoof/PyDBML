from typing import Union

from pydbml.classes import Enum, Table
from pydbml.constants import DEFAULT_SCHEMA


def get_full_name(model: Union[Table, Enum]) -> str:
    """Return the fully-qualified quoted name for a Table or Enum.

    Omits the schema prefix when it is the default schema.
    """
    if model.schema == DEFAULT_SCHEMA:
        return f'"{model.name}"'
    return f'"{model.schema}"."{model.name}"'
