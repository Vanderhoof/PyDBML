from typing import List, Any

from pydbml.classes import Index, Expression, Column
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml, note_option_to_dbml


def render_subjects(source_subjects: List[Any]) -> str:
    subjects = []

    for subj in source_subjects:
        if isinstance(subj, Column):
            subjects.append(subj.name)
        elif isinstance(subj, Expression):
            subjects.append(DefaultDBMLRenderer.render(subj))
        else:
            subjects.append(subj)

    if len(subjects) > 1:
        return f'({", ".join(subj for subj in subjects)})'
    else:
        return subjects[0]


def render_options(model: Index) -> str:
    options = []
    if model.name:
        options.append(f"name: '{model.name}'")
    if model.pk:
        options.append('pk')
    if model.unique:
        options.append('unique')
    if model.type:
        options.append(f'type: {model.type}')
    if model.note:
        options.append(note_option_to_dbml(model.note))

    if options:
        return f' [{", ".join(options)}]'
    return ''


@DefaultDBMLRenderer.renderer_for(Index)
def render_index(model: Index) -> str:
    return (
        (comment_to_dbml(model.comment) if model.comment else '')
        + render_subjects(model.subjects)
        + render_options(model)
    )
