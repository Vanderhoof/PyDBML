import pyparsing as pp
from definitions.table import table
from definitions.reference import ref


class DBMLParser:
    def __init__(self):
        self.tables = []
        self.refs = []

        pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

        table_expr = table.copy()
        ref_expr = ref.copy()

        table_expr.addParseAction(self._parse_table)
        ref_expr.addParseAction(self._parse_ref)

        expr = table_expr | ref_expr
        self._syntax = expr[...]

    def _parse_table(self, s, l, t):
        self.tables.append(t[0])
        self.refs.extend(c.ref for c in t[0].columns if c.ref)

    def _parse_ref(self, s, l, t):
        self.refs.append(t[0])

    def parse_file(self, filename: str):
        self._syntax.parseFile(filename)
