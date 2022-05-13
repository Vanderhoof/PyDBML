from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from .classes import Enum
from .classes import Project
from .classes import Reference
from .classes import Table
from .classes import TableGroup
from .exceptions import SchemaValidationError


class Schema:
    def __init__(self) -> None:
        self.tables: List['Table'] = []
        self.table_dict: Dict[str, 'Table'] = {}
        self.refs: List['Reference'] = []
        self.enums: List['Enum'] = []
        self.table_groups: List['TableGroup'] = []
        self.project: Optional['Project'] = None

    def __repr__(self) -> str:
        return f"<Schema>"

    def __getitem__(self, k: Union[int, str]) -> Table:
        if isinstance(k, int):
            return self.tables[k]
        else:
            return self.table_dict[k]

    def __iter__(self):
        return iter(self.tables)

    def _set_schema(self, obj: Any) -> None:
        obj.schema = self

    def _unset_schema(self, obj: Any) -> None:
        obj.schema = None

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
        if obj.name in self.table_dict:
            raise SchemaValidationError(f'Table {obj.name} is already in the schema.')
        if obj.alias and obj.alias in self.table_dict:
            raise SchemaValidationError(f'Table {obj.alias} is already in the schema.')
        if obj in self.tables:
            raise SchemaValidationError(f'{obj} is already in the schema.')

        self._set_schema(obj)

        self.tables.append(obj)
        self.table_dict[obj.name] = obj
        if obj.alias:
            self.table_dict[obj.alias] = obj
        return obj

    def add_reference(self, obj: Reference):
        for col in (*obj.col1, *obj.col2):
            if col.table.schema == self:
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
        if self.project:
            self.delete_project()
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
        self._unset_schema(self.tables.pop(index))
        result = self.table_dict.pop(obj.name)
        if obj.alias:
            self.table_dict.pop(obj.alias)
        return result

    def delete_reference(self, obj: Reference) -> Reference:
        try:
            index = self.refs.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        result = self.refs.pop(index)
        self._unset_schema(result)
        return result

    def delete_enum(self, obj: Enum) -> Enum:
        try:
            index = self.enums.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        result = self.enums.pop(index)
        self._unset_schema(result)
        return result

    def delete_table_group(self, obj: TableGroup) -> TableGroup:
        try:
            index = self.table_groups.index(obj)
        except ValueError:
            raise SchemaValidationError(f'{obj} is not in the schema.')
        result = self.table_groups.pop(index)
        self._unset_schema(result)
        return result

    def delete_project(self) -> Project:
        if self.project is None:
            raise SchemaValidationError(f'Project is not set.')
        result = self.project
        self.project = None
        self._unset_schema(result)
        return result

    @property
    def sql(self):
        '''Returs SQL of the parsed results'''
        refs = (ref for ref in self.refs if not ref.inline)
        components = (i.sql for i in (*self.enums, *self.tables, *refs))
        return '\n\n'.join(components)

    @property
    def dbml(self):
        '''Generates DBML code out of parsed results'''
        items = (self.project) if self.project else ()
        refs = (ref for ref in self.refs if not ref.inline)
        items.extend((*self.enums, *self.tables, *refs, *self.table_groups))
        components = (
            i.dbml for i in items
        )
        return '\n\n'.join(components)
