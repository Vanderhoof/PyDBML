from __future__ import annotations
import pyparsing as pp
from pathlib import PosixPath
from io import TextIOWrapper
from pydbml.definitions.table import table
from pydbml.definitions.reference import ref
from pydbml.definitions.enum import enum
from pydbml.definitions.table_group import table_group
from pydbml.definitions.project import project
from pydbml.classes import Table, TableReference, Reference


pp.ParserElement.setDefaultWhitespaceChars(' \t\r')


class TableNotFoundError(Exception):
    pass


class ColumnNotFoundError(Exception):
    pass


class PyDBML:
    def __new__(cls,
                source_: str or PosixPath or TextIOWrapper or None = None):
        if source_ is not None:
            if isinstance(source_, str):
                source = source_
            elif isinstance(source_, PosixPath):
                with open(source_, encoding='utf8') as f:
                    source = f.read()
            else:  # TextIOWrapper
                source = source_.read()
            return cls.parse(source)
        else:
            return super().__new__(cls)

    def __repr__(self):
        return "<PyDBML>"

    @staticmethod
    def parse(text: str) -> PyDBMLParseResults:
        return PyDBMLParseResults(text)

    @staticmethod
    def parse_file(file: str or PosixPath or TextIOWrapper):
        if isinstance(file, TextIOWrapper):
            source = file.read()
        else:
            with open(file, encoding='utf8') as f:
                source = f.read()
        return PyDBMLParseResults(source)


class PyDBMLParseResults:
    def __init__(self, source: str):
        self.tables = []
        self.table_dict = {}
        self.refs = []
        self.enums = []
        self.table_groups = []
        self.project = None
        self.source = source

        self._set_syntax()
        self._syntax.parseString(self.source, parseAll=True)
        self._validate()
        self._add_table_refs()
        self._set_enum_types()

    def __repr__(self):
        return "<PyDBMLParseResults>"

    def _set_syntax(self):
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

        expr = (
            table_expr |
            ref_expr |
            enum_expr |
            table_group_expr |
            project_expr
        )
        self._syntax = expr[...]

    def __getitem__(self, k: int or str) -> Table:
        if isinstance(k, int):
            return self.tables[k]
        else:
            return self.table_dict[k]

    def __iter__(self):
        return iter(self.tables)

    def _parse_table(self, s, l, t):
        table = t[0]
        self.tables.append(table)
        for col in table.columns:
            self.refs.extend(col.refs)
        self.table_dict[table.name] = table

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

    def _add_table_refs(self):
        for ref_ in self.refs:
            if ref_.type in (Reference.MANY_TO_ONE, Reference.ONE_TO_ONE):
                table = self.table_dict[ref_.table1]
                init_dict = {
                    'col': ref_.col1,
                    'ref_table': ref_.table2,
                    'ref_col': ref_.col2,
                    'on_update': ref_.on_update,
                    'on_delete': ref_.on_delete
                }
                if ref_.name:
                    init_dict['name'] = ref_.name
            else:
                table = self.table_dict[ref_.table2]
                init_dict = {
                    'col': ref_.col2,
                    'ref_table': ref_.table1,
                    'ref_col': ref_.col1,
                    'on_update': ref_.on_update,
                    'on_delete': ref_.on_delete
                }
                if ref_.name:
                    init_dict['name'] = ref_.name
            table.refs.append(
                TableReference(**init_dict)
            )

    def _set_enum_types(self):
        enum_dict = {enum.name: enum for enum in self.enums}
        for table_ in self.tables:
            for col in table_:
                if str(col.type) in enum_dict:
                    col.type = enum_dict[str(col.type)].get_type()

    def _validate(self):
        for ref_ in self.refs:
            try:
                table1 = self.table_dict[ref_.table1]
            except KeyError:
                raise TableNotFoundError(f"Can't find table \"{ref_.table1}\"")
            for col in table1:
                if ref_.col1 == col.name:
                    break
            else:
                raise ColumnNotFoundError(f'Can\'t find column "{ref_.col1}" in table "{ref_.table1}"')

            try:
                table2 = self.table_dict[ref_.table2]
            except KeyError:
                raise TableNotFoundError(f"Can't find table \"{ref_.table2}\"")
            for col in table2:
                if ref_.col2 == col.name:
                    break
            else:
                raise ColumnNotFoundError(f'Can\'t find column "{ref_.col2}" in table "{ref_.table2}"')

    @property
    def sql(self):
        components = (i.sql for i in (*self.enums, *self.tables))
        return '\n'.join(components)
