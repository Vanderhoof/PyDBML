import pyparsing as pp
from definitions.common import _
from definitions.table import table
from definitions.reference import ref
from definitions.enum import enum
from definitions.table_group import table_group
from definitions.project import project


pp.ParserElement.setDefaultWhitespaceChars(' \t\r')


class DBMLParser:
    def __init__(self):
        self.tables = []
        self.refs = []
        self.enums = []
        self.table_groups = []
        self.projects = []

        table_expr = table.copy()
        ref_expr = ref.copy()
        enum_expr = enum.copy()
        table_group_expr = table_group.copy()
        project_expr = project.copy()

        table_expr.addParseAction(self._parse_table)
        ref_expr.addParseAction(self._parse_ref)
        enum_expr.addParseAction(self._parse_enum)
        table_group_expr.addParseAction(self._parse_table_group)
        project_expr.addParseAction(self._parse_project)

        expr = _ + (
            table_expr |
            ref_expr |
            enum_expr |
            table_group_expr |
            project_expr
        ) + _
        self._syntax = expr[...]

    def _parse_table(self, s, l, t):
        self.tables.append(t[0])
        self.refs.extend(c.ref for c in t[0].columns if c.ref)

    def _parse_ref(self, s, l, t):
        self.refs.append(t[0])

    def _parse_enum(self, s, l, t):
        self.enums.append(t[0])

    def _parse_table_group(self, s, l, t):
        self.table_groups.append(t[0])

    def _parse_project(self, s, l, t):
        self.projects.append(t[0])

    def parse_file(self, filename: str):
        self._syntax.parseFile(filename, parseAll=True)
