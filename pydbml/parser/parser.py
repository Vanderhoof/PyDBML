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

        return PyDBMLParser(text)

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
        parser.parse()
        return parser


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
            self.schema.add(project.build())
        for ref_bp in self.refs:
            self.schema.add(ref_bp.build())


# class Temp:
#     def _parse_table(self, s, l, t):
#         table = t[0]
#         self.schema.add_table(table)
#         for col in table.columns:
#             self.ref_blueprints.extend(col.ref_blueprints)

#     def _parse_ref_blueprint(self, s, l, t):
#         self.ref_blueprints.append(t[0])

#     def _parse_enum(self, s, l, t):
#         self.schema.add_enum(t[0])

#     def _parse_table_group(self, s, l, t):
#         self.table_groups.append(t[0])

#     def _parse_project(self, s, l, t):
#         self.schema.add_project(t[0])

#     def _process_refs(self):
#         '''
#         Fill up the `refs` attribute with Reference object, created from
#         reference blueprints;
#         Add TableReference objects to each table which has references.
#         Validate refs at the same time.
#         '''
#         self.schema._build_refs_from_blueprints(self.ref_blueprints)

#     def _set_enum_types(self):
#         enum_dict = {enum.name: enum for enum in self.schema.enums}
#         for table_ in self.schema.tables:
#             for col in table_:
#                 col_type = str(col.type).strip('"')
#                 if col_type in enum_dict:
#                     col.type = enum_dict[col_type]

#     def _validate(self):
#         self._validate_table_groups()

#     def _validate_table_groups(self):
#         '''
#         Check that all tables, mentioned in the table groups, exist
#         '''
#         for tg in self.table_groups:
#             for table_name in tg:
#                 if table_name not in self.schema.tables_dict:
#                     raise TableNotFoundError(f'Cannot add Table Group "{tg.name}": table "{table_name}" not found.')

#     def _process_table_groups(self):
#         '''
#         Fill up each TableGroup's `item` attribute with references to actual tables.
#         '''
#         for tg in self.table_groups:
#             tg.items = [self.schema.tables_dict[i] for i in tg.items]
#             self.schema.add_table_group(tg)

#     @property
#     def sql(self):
#         '''Returs SQL of the parsed results'''

#         components = (i.sql for i in (*self.enums, *self.tables))
#         return '\n\n'.join(components)

#     @property
#     def dbml(self):
#         '''Generates DBML code out of parsed results'''
#         items = [self.project] if self.project else []
#         items.extend((*self.tables, *self.refs, *self.enums, *self.table_groups))
#         components = (
#             i.dbml for i in items
#         )
#         return '\n\n'.join(components)
