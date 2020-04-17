from __future__ import annotations
import os
import pyparsing as pp
from pathlib import PosixPath
from io import TextIOWrapper
from definitions.common import _
from definitions.table import table
from definitions.reference import ref
from definitions.enum import enum
from definitions.table_group import table_group
from definitions.project import project


pp.ParserElement.setDefaultWhitespaceChars(' \t\r')


class PyDBML:
    def __init__(self,
                 source_: str or PosixPath or TextIOWrapper or None = None):
        if source_ is not None:
            if isinstance(source_, str):
                if os.path.isfile(source_):
                    with open(source_, encoding='utf8') as f:
                        source = f.read()
                else:
                    source = source_
            elif isinstance(source_, PosixPath):
                with open(source_, encoding='utf8') as f:
                    source = f.read()
            else:  # TextIOWrapper
                source = source_.read()
            return self.parse(source)

    def parse(self, text: str) -> DBMLParseResults:
        result = DBMLParseResults()
        _ = result._syntax.parseString(text, parseAll=True)
        return result

    def parse_file(self,
                   file: str or PosixPath or TextIOWrapper):
        if isinstance(file, TextIOWrapper):
            return self.parse(file.read())
        else:
            result = DBMLParseResults()
            _ = result._syntax.parseFile(file, parseAll=True)
            return result


class DBMLParseResults:
    def __init__(self):
        self.tables = []
        self.refs = []
        self.enums = []
        self.table_groups = []
        self.project = None

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
        if not self.project:
            self.project = t[0]
        else:
            raise SyntaxError('Project redifinition not allowed')

