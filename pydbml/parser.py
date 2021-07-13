from __future__ import annotations

import pyparsing as pp

from io import TextIOWrapper
from pathlib import Path

from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from .classes import Enum
from .classes import Project
from .classes import Reference
from .classes import ReferenceBlueprint
from .classes import Table
from .classes import TableGroup
from .classes import TableReference
from .definitions.common import _
from .definitions.common import comment
from .definitions.enum import enum
from .definitions.project import project
from .definitions.reference import ref
from .definitions.table import table
from .definitions.table_group import table_group
from .exceptions import ColumnNotFoundError
from .exceptions import TableNotFoundError

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
    def parse(text: str) -> PyDBMLParseResults:
        if text[0] == '\ufeff':  # removing BOM
            text = text[1:]
        return PyDBMLParseResults(text)

    @staticmethod
    def parse_file(file: Union[str, Path, TextIOWrapper]):
        if isinstance(file, TextIOWrapper):
            source = file.read()
        else:
            with open(file, encoding='utf8') as f:
                source = f.read()
        if source[0] == '\ufeff':  # removing BOM
            source = source[1:]
        return PyDBMLParseResults(source)


class PyDBMLParseResults:
    def __init__(self, source: str):
        self.tables: List[Table] = []
        self.table_dict: Dict[str, Table] = {}
        self.refs: List[Reference] = []
        self.ref_blueprints: List[ReferenceBlueprint] = []
        self.enums: List[Enum] = []
        self.table_groups: List[TableGroup] = []
        self.project: Optional[Project] = None
        self.source = source

        self._set_syntax()
        self._syntax.parseString(self.source, parseAll=True)
        self._validate()
        self._process_refs()
        self._process_table_groups()
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
        ref_expr.addParseAction(self._parse_ref_blueprint)
        enum_expr.addParseAction(self._parse_enum)
        table_group_expr.addParseAction(self._parse_table_group)
        project_expr.addParseAction(self._parse_project)

        expr = (
            table_expr
            | ref_expr
            | enum_expr
            | table_group_expr
            | project_expr
        )
        self._syntax = expr[...] + ('\n' | comment)[...] + pp.StringEnd()

    def __getitem__(self, k: Union[int, str]) -> Table:
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
            self.ref_blueprints.extend(col.ref_blueprints)
        self.table_dict[table.name] = table

    def _parse_ref_blueprint(self, s, l, t):
        self.ref_blueprints.append(t[0])

    def _parse_enum(self, s, l, t):
        self.enums.append(t[0])

    def _parse_table_group(self, s, l, t):
        self.table_groups.append(t[0])

    def _parse_project(self, s, l, t):
        if not self.project:
            self.project = t[0]
        else:
            raise SyntaxError('Project redifinition not allowed')

    def _process_refs(self):
        '''
        Fill up the `refs` attribute with Reference object, created from
        reference blueprints;
        Add TableReference objects to each table which has references.
        Validate refs at the same time.
        '''
        for ref_ in self.ref_blueprints:
            for tb in self.tables:
                if tb.name == ref_.table1 or tb.alias == ref_.table1:
                    table1 = tb
                    break
            else:
                raise TableNotFoundError('Error while parsing reference:'
                                         f'table "{ref_.table1}"" is not defined.')
            for tb in self.tables:
                if tb.name == ref_.table2 or tb.alias == ref_.table2:
                    table2 = tb
                    break
            else:
                raise TableNotFoundError('Error while parsing reference:'
                                         f'table "{ref_.table2}"" is not defined.')
            col1_names = [c.strip('() ') for c in ref_.col1.split(',')]
            col1 = []
            for col_name in col1_names:
                try:
                    col1.append(table1[col_name])
                except KeyError:
                    raise ColumnNotFoundError('Error while parsing reference:'
                                              f'column "{col_name} not defined in table "{table1.name}".')
            col2_names = [c.strip('() ') for c in ref_.col2.split(',')]
            col2 = []
            for col_name in col2_names:
                try:
                    col2.append(table2[col_name])
                except KeyError:
                    raise ColumnNotFoundError('Error while parsing reference:'
                                              f'column "{col_name} not defined in table "{table2.name}".')
            self.refs.append(
                Reference(
                    ref_.type,
                    table1,
                    col1,
                    table2,
                    col2,
                    name=ref_.name,
                    comment=ref_.comment,
                    on_update=ref_.on_update,
                    on_delete=ref_.on_delete
                )
            )

            if ref_.type in (Reference.MANY_TO_ONE, Reference.ONE_TO_ONE):
                table = table1
                init_dict = {
                    'col': col1,
                    'ref_table': table2,
                    'ref_col': col2,
                    'name': ref_.name,
                    'on_update': ref_.on_update,
                    'on_delete': ref_.on_delete
                }
            else:
                table = table2
                init_dict = {
                    'col': col2,
                    'ref_table': table1,
                    'ref_col': col1,
                    'name': ref_.name,
                    'on_update': ref_.on_update,
                    'on_delete': ref_.on_delete
                }
            table.add_ref(
                TableReference(**init_dict)
            )

    def _set_enum_types(self):
        enum_dict = {enum.name: enum for enum in self.enums}
        for table_ in self.tables:
            for col in table_:
                if str(col.type) in enum_dict:
                    col.type = enum_dict[str(col.type)].get_type()

    def _validate(self):
        self._validate_table_groups()

    def _validate_table_groups(self):
        '''
        Check that all tables, mentioned in the table groups, exist
        '''
        for tg in self.table_groups:
            for table_name in tg:
                if table_name not in self.table_dict:
                    raise TableNotFoundError(f'Cannot add Table Group "{tg.name}": table "{table_name}" not found.')

    def _process_table_groups(self):
        '''
        Fill up each TableGroup's `item` attribute with references to actual tables.
        '''
        for tg in self.table_groups:
            tg.items = [self[i] for i in tg.items]

    @property
    def sql(self):
        '''Returs SQL of the parsed results'''

        components = (i.sql for i in (*self.enums, *self.tables))
        return '\n\n'.join(components)

    @property
    def dbml(self):
        '''Generates DBML code out of parsed results'''
        items = [self.project] if self.project else []
        items.extend((*self.tables, *self.refs, *self.enums, *self.table_groups))
        components = (
            i.dbml for i in items
        )
        return '\n\n'.join(components)
