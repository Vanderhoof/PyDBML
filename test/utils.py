from unittest.mock import  Mock
from typing import Optional


DEFAULT_OPTIONS = {
    'reformat_notes': True,
}

def mock_parser(options: Optional[dict] = None):
    if options is None:
        options = dict(DEFAULT_OPTIONS)
    return Mock(options=options)
