from .classes import Enum
from .classes import Project
from .classes import Reference
from .classes import Table
from .classes import TableGroup
from pydbml.parser.blueprints import ReferenceBlueprint
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import TableNotFoundError
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class SchemaValidationError(Exception):
    pass


class Schema:
    def __init__(self) -> None:
        self.tables: List[Table] = []
        self.tables_dict: Dict[str, Table] = {}
        self.refs: List[Reference] = []
        # self.ref_blueprints: List[ReferenceBlueprint] = []
        self.enums: List[Enum] = []
        self.table_groups: List[TableGroup] = []
        self.project: Optional[Project] = None

    def __repr__(self) -> str:
        return f"<Schema>"

    # def _build_refs_from_blueprints(self, blueprints: List[ReferenceBlueprint]):
    #     '''
    #     Fill up the `refs` attribute with Reference object, created from
    #     reference blueprints;
    #     Add TableReference objects to each table which has references.
    #     Validate refs at the same time.
    #     '''
    #     for ref_ in blueprints:
    #         for table_ in self.tables:
    #             if table_.name == ref_.table1 or table_.alias == ref_.table1:
    #                 table1 = table_
    #                 break
    #         else:
    #             raise TableNotFoundError('Error while parsing reference:'
    #                                      f'table "{ref_.table1}"" is not defined.')
    #         for table_ in self.tables:
    #             if table_.name == ref_.table2 or table_.alias == ref_.table2:
    #                 table2 = table_
    #                 break
    #         else:
    #             raise TableNotFoundError('Error while parsing reference:'
    #                                      f'table "{ref_.table2}"" is not defined.')
    #         col1_names = [c.strip('() ') for c in ref_.col1.split(',')]
    #         col1 = []
    #         for col_name in col1_names:
    #             try:
    #                 col1.append(table1[col_name])
    #             except KeyError:
    #                 raise ColumnNotFoundError('Error while parsing reference:'
    #                                           f'column "{col_name} not defined in table "{table1.name}".')
    #         col2_names = [c.strip('() ') for c in ref_.col2.split(',')]
    #         col2 = []
    #         for col_name in col2_names:
    #             try:
    #                 col2.append(table2[col_name])
    #             except KeyError:
    #                 raise ColumnNotFoundError('Error while parsing reference:'
    #                                           f'column "{col_name} not defined in table "{table2.name}".')
    #         self.add_reference(
    #             Reference(
    #                 ref_.type,
    #                 table1,
    #                 col1,
    #                 table2,
    #                 col2,
    #                 name=ref_.name,
    #                 comment=ref_.comment,
    #                 on_update=ref_.on_update,
    #                 on_delete=ref_.on_delete
    #             )
    #         )

    def _set_schema(self, obj: Any) -> None:
        obj.schema = self

    def add(self, obj: Any) -> Any:
        if isinstance(obj, Table):
            return self.add_table(obj)
        elif isinstance(obj, Reference):
            return self.add_reference(obj)
        elif isinstance(obj, Enum):
            return self.add_enum(obj)
        elif isinstance(obj, TableGroup):
            return self.add_table_group(obj)
        elif isinstance(obj, Project):
            return self.add_project(obj)
        else:
            raise SchemaValidationError(f'Unsupported type {type(obj)}.')

    def add_table(self, obj: Table) -> Table:
        if obj.name in self.tables_dict:
            raise SchemaValidationError(f'Table {obj.name} is already in the schema.')
        if obj in self.tables:
            raise SchemaValidationError(f'{obj} is already in the schema.')

        self._set_schema(obj)

        self.tables.append(obj)
        self.tables_dict[obj.name] = obj
        return obj

    def add_reference(self, obj: Reference):
        for table in (obj.table1, obj.table2):
            if table in self.tables:
                break
        else:
            raise SchemaValidationError(
                'Cannot add reference. At least one of the referenced tables'
                ' should belong to this schema'
            )
        if obj in self.refs:
            raise SchemaValidationError(f'{obj} is already in the schema.')

        self._set_schema(obj)
        self.refs.append(obj)
        return obj

    def add_enum(self, obj: Enum) -> Enum:
        for enum in self.enums:
            if enum.name == obj.name:
                raise SchemaValidationError(f'Enum {obj.name} is already in the schema.')
        if obj in self.enums:
            raise SchemaValidationError(f'{obj} is already in the schema.')

        self._set_schema(obj)
        self.enums.append(obj)
        return obj

    def add_table_group(self, obj: TableGroup) -> TableGroup:
        for table_group in self.table_groups:
            if table_group.name == obj.name:
                raise SchemaValidationError(f'TableGroup {obj.name} is already in the schema.')
        if obj in self.table_groups:
            raise SchemaValidationError(f'{obj} is already in the schema.')

        self._set_schema(obj)
        self.table_groups.append(obj)
        return obj

    def add_project(self, obj: Project) -> Project:
        self._set_schema(obj)
        self.project = obj
        return obj

    def delete(self, obj: Any) -> Any:
        if isinstance(obj, Table):
            return self.delete_table(obj)
        elif isinstance(obj, Reference):
            return self.delete_reference(obj)
        elif isinstance(obj, Enum):
            return self.delete_enum(obj)
        elif isinstance(obj, TableGroup):
            return self.delete_table_group(obj)
        elif isinstance(obj, Project):
            return self.delete_project()
        else:
            raise SchemaValidationError(f'Unsupported type {type(obj)}.')

    def delete_table(self, obj: Table) -> Table:
        try:
            index = self.tables.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        self.tables.pop(index).schema = None
        return self.tables_dict.pop(obj.name)

    def delete_reference(self, obj: Reference) -> Reference:
        try:
            index = self.refs.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        result = self.refs.pop(index)
        result.schema = None
        return result

    def delete_enum(self, obj: Enum) -> Enum:
        try:
            index = self.enums.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        result = self.enums.pop(index)
        result.schema = None
        return result

    def delete_table_group(self, obj: TableGroup) -> TableGroup:
        try:
            index = self.tables_groups.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        result = self.table_groups.pop(index)
        result.schema = None
        return result

    def delete_project(self) -> Project:
        if self.Project is None:
            raise SchemaValidationError(f'Project is not set.')
        result = self.Project
        self.Project = None
        result.schema = None
        return result
