from __future__ import annotations

import pyparsing as pp

from io import TextIOWrapper
from pathlib import Path

from typing import List
from typing import Optional
from typing import Union

from .blueprints import EnumBlueprint
from .blueprints import ProjectBlueprint
from .blueprints import ReferenceBlueprint
from .blueprints import TableBlueprint
from .blueprints import TableGroupBlueprint
from pydbml.classes import Table
from pydbml.definitions.common import comment
from pydbml.definitions.enum import enum
from pydbml.definitions.project import project
from pydbml.definitions.reference import ref
from pydbml.definitions.table import table
from pydbml.definitions.table_group import table_group
from pydbml.exceptions import TableNotFoundError
from pydbml.schema import Schema

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')


class PyDBML:
    '''
    PyDBML parser factory. If properly initiated, returns PyDBMLParseResults
    which contains parse results in attributes.

    Usage option 1:

    >>> with open('schema.dbml') as f:
    ...     p = PyDBML(f)
    ...     # or
    ...     p = PyDBML(f.read())

    Usage option 2:
    >>> p = PyDBML.parse_file('schema.dbml')
    >>> # or
    >>> from pathlib import Path
    >>> p = PyDBML(Path('schema.dbml'))
    '''

    def __new__(cls,
                source_: Optional[Union[str, Path, TextIOWrapper]] = None):
        if source_ is not None:
            if isinstance(source_, str):
                source = source_
            elif isinstance(source_, Path):
                with open(source_, encoding='utf8') as f:
                    source = f.read()
            else:  # TextIOWrapper
                source = source_.read()
            if source[0] == '\ufeff':  # removing BOM
                source = source[1:]
            return cls.parse(source)
        else:
            return super().__new__(cls)

    def __repr__(self):
        return "<PyDBML>"

    @staticmethod
    def parse(text: str) -> PyDBMLParser:
        if text[0] == '\ufeff':  # removing BOM
            text = text[1:]

        parser = PyDBMLParser(text)
        return parser.parse()

    @staticmethod
    def parse_file(file: Union[str, Path, TextIOWrapper]) -> PyDBMLParser:
        if isinstance(file, TextIOWrapper):
            source = file.read()
        else:
            with open(file, encoding='utf8') as f:
                source = f.read()
        if source[0] == '\ufeff':  # removing BOM
            source = source[1:]
        parser = PyDBMLParser(source)
        return parser.parse()


def parse(source: str):
    parser = PyDBMLParser(source)
    return parser.parse()


class PyDBMLParser:
    def __init__(self, source: str):
        self.schema = None

        self.ref_blueprints: List[ReferenceBlueprint] = []
        self.table_groups = []
        self.source = source
        self.tables = []
        self.refs = []
        self.enums = []
        self.table_groups = []
        self.project = None

    def parse(self):
        self._set_syntax()
        self._syntax.parseString(self.source, parseAll=True)
        self.build_schema()
        return self.schema

    def __repr__(self):
        return "<PyDBMLParser>"

    def _set_syntax(self):
        table_expr = table.copy()
        ref_expr = ref.copy()
        enum_expr = enum.copy()
        table_group_expr = table_group.copy()
        project_expr = project.copy()

        table_expr.addParseAction(self.parse_blueprint)
        ref_expr.addParseAction(self.parse_blueprint)
        enum_expr.addParseAction(self.parse_blueprint)
        table_group_expr.addParseAction(self.parse_blueprint)
        project_expr.addParseAction(self.parse_blueprint)

        expr = (
            table_expr
            | ref_expr
            | enum_expr
            | table_group_expr
            | project_expr
        )
        self._syntax = expr[...] + ('\n' | comment)[...] + pp.StringEnd()

    def parse_blueprint(self, s, l, t):
        blueprint = t[0]
        if isinstance(blueprint, TableBlueprint):
            self.tables.append(blueprint)
            ref_bps = blueprint.get_reference_blueprints()
            col_bps = blueprint.columns or []
            index_bps = blueprint.indexes or []
            for ref_bp in ref_bps:
                self.refs.append(ref_bp)
                ref_bp.parser = self
            for col_bp in col_bps:
                col_bp.parser = self
            for index_bp in index_bps:
                index_bp.parser = self
        elif isinstance(blueprint, ReferenceBlueprint):
            self.refs.append(blueprint)
        elif isinstance(blueprint, EnumBlueprint):
            self.enums.append(blueprint)
        elif isinstance(blueprint, TableGroupBlueprint):
            self.table_groups.append(blueprint)
        elif isinstance(blueprint, ProjectBlueprint):
            self.project = blueprint
        else:
            raise RuntimeError(f'type unknown: {blueprint}')
        blueprint.parser = self

    def locate_table(self, name: str) -> 'Table':
        if not self.schema:
            raise RuntimeError('Schema is not ready')
        try:
            result = self.schema[name]
        except KeyError:
            raise TableNotFoundError(f'Table {name} not present in the schema')
        return result

    def build_schema(self):
        self.schema = Schema()
        for enum_bp in self.enums:
            self.schema.add(enum_bp.build())
        for table_bp in self.tables:
            self.schema.add(table_bp.build())
            self.ref_blueprints.extend(table_bp.get_reference_blueprints())
        for table_group_bp in self.table_groups:
            self.schema.add(table_group_bp.build())
        if self.project:
            self.schema.add(self.project.build())
        for ref_bp in self.refs:
            self.schema.add(ref_bp.build())
