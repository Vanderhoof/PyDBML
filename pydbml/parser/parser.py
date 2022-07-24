from __future__ import annotations
from io import TextIOWrapper
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import pyparsing as pp

from .blueprints import EnumBlueprint
from .blueprints import ProjectBlueprint
from .blueprints import ReferenceBlueprint
from .blueprints import TableBlueprint
from .blueprints import TableGroupBlueprint
from pydbml.classes import Table
from pydbml.database import Database
from pydbml.definitions.common import comment
from pydbml.definitions.enum import enum
from pydbml.definitions.project import project
from pydbml.definitions.reference import ref
from pydbml.definitions.table import table
from pydbml.definitions.table_group import table_group
from pydbml.exceptions import TableNotFoundError
from pydbml.tools import remove_bom


pp.ParserElement.set_default_whitespace_chars(' \t\r')


class PyDBML:
    '''
    PyDBML parser factory. If properly initiated, returns parsed Database.

    Usage option 1:

    >>> with open('test_schema.dbml') as f:
    ...     p = PyDBML(f)
    ...     # or
    ...     p = PyDBML(f.read())

    Usage option 2:
    >>> p = PyDBML.parse_file('test_schema.dbml')
    >>> # or
    >>> from pathlib import Path
    >>> p = PyDBML(Path('test_schema.dbml'))
    '''

    def __new__(cls, source_: Optional[Union[str, Path, TextIOWrapper]] = None):
        if source_ is not None:
            if isinstance(source_, str):
                source = source_
            elif isinstance(source_, Path):
                with open(source_, encoding='utf8') as f:
                    source = f.read()
            elif isinstance(source_, TextIOWrapper):
                source = source_.read()
            else:
                raise TypeError('Source must be str, path or file stream')

            source = remove_bom(source)
            return cls.parse(source)
        else:
            return super().__new__(cls)

    def __repr__(self):
        """
        >>> PyDBML()
        <PyDBML>
        """

        return "<PyDBML>"

    @staticmethod
    def parse(text: str) -> Database:
        text = remove_bom(text)
        parser = PyDBMLParser(text)
        return parser.parse()

    @staticmethod
    def parse_file(file: Union[str, Path, TextIOWrapper]) -> Database:
        if isinstance(file, TextIOWrapper):
            source = file.read()
        else:
            with open(file, encoding='utf8') as f:
                source = f.read()
        source = remove_bom(source)
        parser = PyDBMLParser(source)
        return parser.parse()


class PyDBMLParser:
    def __init__(self, source: str):
        self.database = None

        self.ref_blueprints: List[ReferenceBlueprint] = []
        self.table_groups: List[TableGroupBlueprint] = []
        self.source = source
        self.tables: List[TableBlueprint] = []
        self.refs: List[ReferenceBlueprint] = []
        self.enums: List[EnumBlueprint] = []
        self.project: Optional[ProjectBlueprint] = None

    def parse(self):
        self._set_syntax()
        self._syntax.parse_string(self.source, parseAll=True)
        self.build_database()
        return self.database

    def __repr__(self):
        """
        >>> PyDBMLParser('')
        <PyDBMLParser>
        """

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

    def parse_blueprint(self, s, loc, tok):
        blueprint = tok[0]
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
                if col_bp.note:
                    col_bp.note.parser = self
            for index_bp in index_bps:
                index_bp.parser = self
                if index_bp.note:
                    index_bp.note.parser = self
            if blueprint.note:
                blueprint.note.parser = self
        elif isinstance(blueprint, ReferenceBlueprint):
            self.refs.append(blueprint)
        elif isinstance(blueprint, EnumBlueprint):
            self.enums.append(blueprint)
            for enum_item in blueprint.items:
                if enum_item.note:
                    enum_item.note.parser = self
        elif isinstance(blueprint, TableGroupBlueprint):
            self.table_groups.append(blueprint)
        elif isinstance(blueprint, ProjectBlueprint):
            self.project = blueprint
            if blueprint.note:
                blueprint.note.parser = self
        else:
            raise RuntimeError(f'type unknown: {blueprint}')
        blueprint.parser = self

    def locate_table(self, schema: str, name: str) -> 'Table':
        if not self.database:
            raise RuntimeError('Database is not ready')
        # first by alias
        result = self.database.table_dict.get(name)
        if result is None:
            full_name = f'{schema}.{name}'
            result = self.database.table_dict.get(full_name)
        if result is None:
            raise TableNotFoundError(f'Table {full_name} not present in the database')
        return result

    def build_database(self):
        self.database = Database()
        for enum_bp in self.enums:
            self.database.add(enum_bp.build())
        for table_bp in self.tables:
            self.database.add(table_bp.build())
            self.ref_blueprints.extend(table_bp.get_reference_blueprints())
        for table_group_bp in self.table_groups:
            self.database.add(table_group_bp.build())
        if self.project:
            self.database.add(self.project.build())
        for ref_bp in self.refs:
            self.database.add(ref_bp.build())
