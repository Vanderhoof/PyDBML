import pyparsing as pp
from definitions.table import table
from definitions.ref import ref


class DBMLParser:
    def __init__(self):
        self.tables = []
        self.refs = []

        table_expr = pp.copy(table)
        ref_expr = pp.copy(ref)
        table_expr.setParseAction(self._parse_table)

        expr = table_expr | ref_expr
        self._syntax = expr[...]

    def _parse_table(self, s, l, t):
        self.tables.append()
