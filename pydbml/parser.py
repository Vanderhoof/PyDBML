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
from pydbml.exceptions import TableNotFoundError, ColumnNotFoundError

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
                source_: str or PosixPath or TextIOWrapper or None = None):
        if source_ is not None:
            if isinstance(source_, str):
                source = source_
            elif isinstance(source_, PosixPath):
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
    def parse_file(file: str or PosixPath or TextIOWrapper):
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
        self.tables = []
        self.table_dict = {}
        self.refs = []
        self.ref_blueprints = []
        self.enums = []
        self.table_groups = []
        self.project = None
        self.source = source

        self._set_syntax()
        self._syntax.parseString(self.source, parseAll=True)
        self._validate()
        self._process_refs()
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
            table1 = self.table_dict.get(ref_.table1)
            if not table1:
                raise TableNotFoundError('Error while parsing reference:'
                                         f'table "{ref_.table1}"" is not defined.')
            table2 = self.table_dict.get(ref_.table2)
            if not table2:
                raise TableNotFoundError('Error while parsing reference:'
                                         f'table "{ref_.table2}"" is not defined.')
            col1 = table1.get(ref_.col1)
            if not col1:
                raise ColumnNotFoundError('Error while parsing reference:'
                                          f'column "{ref_.col1} not defined in table "{table1.name}".')
            col2 = table2.get(ref_.col2)
            if not col2:
                raise ColumnNotFoundError('Error while parsing reference:'
                                          f'column "{ref_.col2} not defined in table "{table2.name}".')
            self.refs.append(
                Reference(
                    ref_.type,
                    table1,
                    col1,
                    table2,
                    col2,
                    name=ref_.name,
                    comment=ref_.comment,
                    on_update=ref_.on_delete,
                    on_delete=ref_.on_update
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
        self._validate_table_groups()

    def _validate_table_groups(self):
        '''
        Check that all tables, mentioned in the table groups, exist
        '''
        for tg in self.table_groups:
            for table_name in tg:
                if table_name not in self.table_dict:
                    raise TableNotFoundError(f'Cannot add Table Group "{tg.name}": table "{table_name}" not found.')

    @property
    def sql(self):
        '''Returs SQL of the parsed results'''

        components = (i.sql for i in (*self.enums, *self.tables))
        return '\n'.join(components)
