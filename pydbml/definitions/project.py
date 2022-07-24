import pyparsing as pp

from .common import _
from .common import _c
from .common import n
from .common import note
from .common import note_object
from .generic import name
from .generic import string_literal
from pydbml.parser.blueprints import NoteBlueprint
from pydbml.parser.blueprints import ProjectBlueprint

pp.ParserElement.set_default_whitespace_chars(' \t\r')

project_field = pp.Group(name + _ + pp.Suppress(':') + _ - string_literal)

project_element = _ + (note | note_object | project_field) + _

project_body = project_element[...]

project = _c + (
    pp.CaselessLiteral('project') + _
    - name('name') + _
    + '{' + _
    - project_body('items') + _
    - '}'
) + (n | pp.StringEnd())


def parse_project(s, loc, tok):
    '''
    Project project_name {
      database_type: 'PostgreSQL'
      Note: 'Description of the project'
    }
    '''
    init_dict = {'name': tok['name']}
    items = {}
    for item in tok.get('items', []):
        if isinstance(item, NoteBlueprint):
            init_dict['note'] = item
        else:
            k, v = item
            items[k] = v
    if items:
        init_dict['items'] = items
    if 'comment_before' in tok:
        comment = '\n'.join(c[0] for c in tok['comment_before'])
        init_dict['comment'] = comment
    return ProjectBlueprint(**init_dict)


project.set_parse_action(parse_project)
