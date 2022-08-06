from dataclasses import dataclass
from typing import Any
from typing import Collection
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from pydbml.classes import Column
from pydbml.classes import Enum
from pydbml.classes import EnumItem
from pydbml.classes import Expression
from pydbml.classes import Index
from pydbml.classes import Note
from pydbml.classes import Project
from pydbml.classes import Reference
from pydbml.classes import Table
from pydbml.classes import TableGroup
from pydbml.exceptions import ColumnNotFoundError
from pydbml.exceptions import TableNotFoundError
from pydbml.tools import remove_indentation
from pydbml.tools import strip_empty_lines


class Blueprint:
    parser = None


@dataclass
class NoteBlueprint(Blueprint):
    text: str

    def _preformat_text(self) -> str:
        '''Preformat the note text for idempotence'''
        result = strip_empty_lines(self.text)
        result = remove_indentation(result)
        return result

    def build(self) -> 'Note':
        text = self._preformat_text()
        return Note(text)


@dataclass
class ExpressionBlueprint(Blueprint):
    text: str

    def build(self) -> Expression:
        return Expression(self.text)


@dataclass
class ReferenceBlueprint(Blueprint):
    type: Literal['>', '<', '-', '<>']
    inline: bool
    name: Optional[str] = None
    schema1: str = 'public'
    table1: Optional[str] = None
    col1: Optional[Union[str, Collection[str]]] = None
    schema2: str = 'public'
    table2: Optional[str] = None
    col2: Optional[Union[str, Collection[str]]] = None
    comment: Optional[str] = None
    on_update: Optional[str] = None
    on_delete: Optional[str] = None

    def build(self) -> 'Reference':
        '''
        both tables and columns should be present before build
        '''
        if self.table1 is None:
            raise TableNotFoundError("Can't build Reference, table1 unknown")
        if self.table2 is None:
            raise TableNotFoundError("Can't build Reference, table2 unknown")
        if self.col1 is None:
            raise ColumnNotFoundError("Can't build Reference, col1 unknown")
        if self.col2 is None:
            raise ColumnNotFoundError("Can't build Reference, col2 unknown")

        if self.parser:
            table1 = self.parser.locate_table(self.schema1, self.table1)
        else:
            raise RuntimeError('Parser is not set')

        col1_list = [c.strip('() ') for c in self.col1.split(',')]
        col1 = [table1[col] for col in col1_list]

        table2 = self.parser.locate_table(self.schema2, self.table2)
        col2_list = [c.strip('() ') for c in self.col2.split(',')]
        col2 = [table2[col] for col in col2_list]

        return Reference(
            type=self.type,
            inline=self.inline,
            col1=col1,
            col2=col2,
            name=self.name,
            comment=self.comment,
            on_update=self.on_update,
            on_delete=self.on_delete
        )


@dataclass
class ColumnBlueprint(Blueprint):
    name: str
    type: str
    unique: bool = False
    not_null: bool = False
    pk: bool = False
    autoinc: bool = False
    default: Optional[Any] = None
    note: Optional[NoteBlueprint] = None
    ref_blueprints: Optional[List[ReferenceBlueprint]] = None
    comment: Optional[str] = None

    def build(self) -> 'Column':
        if isinstance(self.default, ExpressionBlueprint):
            self.default = self.default.build()
        if self.parser:
            if '.' in self.type:
                schema, name = self.type.split('.')
            else:
                schema, name = 'public', self.type
            for enum in self.parser.database.enums:
                if (enum.schema, enum.name) == (schema, name):
                    self.type = enum
                    break
        return Column(
            name=self.name,
            type=self.type,
            unique=self.unique,
            not_null=self.not_null,
            pk=self.pk,
            autoinc=self.autoinc,
            default=self.default,
            note=self.note.build() if self.note else None,
            comment=self.comment
        )


@dataclass
class IndexBlueprint(Blueprint):
    subject_names: List[Union[str, ExpressionBlueprint]]
    name: Optional[str] = None
    unique: bool = False
    type: Optional[Literal['hash', 'btree']] = None
    pk: bool = False
    note: Optional[NoteBlueprint] = None
    comment: Optional[str] = None

    table = None

    def build(self) -> 'Index':
        return Index(
            # TableBlueprint will process subjects
            subjects=[],
            name=self.name,
            unique=self.unique,
            type=self.type,
            pk=self.pk,
            note=self.note.build() if self.note else None,
            comment=self.comment
        )


@dataclass
class TableBlueprint(Blueprint):
    name: str
    schema: str = 'public'
    columns: Optional[List[ColumnBlueprint]] = None
    indexes: Optional[List[IndexBlueprint]] = None
    alias: Optional[str] = None
    note: Optional[NoteBlueprint] = None
    header_color: Optional[str] = None
    comment: Optional[str] = None

    def build(self) -> 'Table':
        result = Table(
            name=self.name,
            schema=self.schema,
            alias=self.alias,
            note=self.note.build() if self.note else None,
            header_color=self.header_color,
            comment=self.comment
        )
        columns = self.columns or []
        indexes = self.indexes or []
        for col_bp in columns:
            result.add_column(col_bp.build())
        for index_bp in indexes:
            index = index_bp.build()
            new_subjects: List[Union[str, Column, Expression]] = []
            for subj in index_bp.subject_names:
                if isinstance(subj, ExpressionBlueprint):
                    new_subjects.append(subj.build())
                else:
                    for col in result.columns:
                        if col.name == subj:
                            new_subjects.append(col)
                            break
                    else:
                        raise ColumnNotFoundError(
                            f'Cannot add index, column "{subj}" not defined in'
                            ' table "{self.name}".'
                        )
            index.subjects = new_subjects
            result.add_index(index)
        return result

    def get_reference_blueprints(self):
        ''' the inline ones '''
        result = []
        for col in self.columns:
            for ref_bp in col.ref_blueprints or []:
                ref_bp.schema1 = self.schema
                ref_bp.table1 = self.name
                ref_bp.col1 = col.name
                result.append(ref_bp)
        return result


@dataclass
class EnumItemBlueprint(Blueprint):
    name: str
    note: Optional[NoteBlueprint] = None
    comment: Optional[str] = None

    def build(self) -> 'EnumItem':
        return EnumItem(
            name=self.name,
            note=self.note.build() if self.note else None,
            comment=self.comment
        )


@dataclass
class EnumBlueprint(Blueprint):
    name: str
    items: List[EnumItemBlueprint]
    schema: str = 'public'
    comment: Optional[str] = None

    def build(self) -> 'Enum':
        return Enum(
            name=self.name,
            items=[ei.build() for ei in self.items],
            schema=self.schema,
            comment=self.comment
        )


@dataclass
class ProjectBlueprint(Blueprint):
    name: str
    items: Optional[Dict[str, str]] = None
    note: Optional[NoteBlueprint] = None
    comment: Optional[str] = None

    def build(self) -> 'Project':
        return Project(
            name=self.name,
            items=dict(self.items) if self.items else {},
            note=self.note.build() if self.note else None,
            comment=self.comment
        )


@dataclass
class TableGroupBlueprint(Blueprint):
    name: str
    items: List[str]
    comment: Optional[str] = None

    def build(self) -> 'TableGroup':
        if not self.parser:
            raise RuntimeError('Parser is not set')
        items = []
        for table_name in self.items:
            components = table_name.split('.')
            schema, table = components if len(components) == 2 else ('public', components[0])
            items.append(self.parser.locate_table(schema, table))
        return TableGroup(
            name=self.name,
            items=items,
            comment=self.comment
        )
