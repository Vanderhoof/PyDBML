from pydbml.classes import Index, Expression, Column
from pydbml.renderer.dbml.default.renderer import DefaultDBMLRenderer
from pydbml.renderer.dbml.default.utils import comment_to_dbml, note_option_to_dbml


@DefaultDBMLRenderer.renderer_for(Index)
def render_index(model: Index) -> str:
    subjects = []

    for subj in model.subjects:
        if isinstance(subj, Column):
            subjects.append(subj.name)
        elif isinstance(subj, Expression):
            subjects.append(DefaultDBMLRenderer.render(subj))
        else:
            subjects.append(subj)

    result = comment_to_dbml(model.comment) if model.comment else ''

    if len(subjects) > 1:
        result += f'({", ".join(subj for subj in subjects)})'
    else:
        result += subjects[0]

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
        result += f' [{", ".join(options)}]'
    return result
