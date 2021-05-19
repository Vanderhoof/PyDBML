import pyparsing as pp

from pydbml.classes import Note
from pydbml.classes import Project

from .common import _
from .common import _c
from .common import n
from .common import note
from .generic import name
from .generic import string_literal

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

project_field = pp.Group(name + _ + pp.Suppress(':') + _ - string_literal)

project_element = _ + (note | project_field) + _

project_body = project_element[...]

project = _c + (
    pp.CaselessLiteral('project') + _
    - name('name') + _
    + '{' + _
    - project_body('items') + _
    - '}'
) + (n | pp.StringEnd())


def parse_project(s, l, t):
    '''
    Project project_name {
      database_type: 'PostgreSQL'
      Note: 'Description of the project'
    }
    '''
    init_dict = {'name': t['name']}
    items = {}
    for item in t.get('items', []):
        if isinstance(item, Note):
            init_dict['note'] = item
        else:
            k, v = item
            items[k] = v
    if items:
        init_dict['items'] = items
    if 'comment_before' in t:
        comment = '\n'.join(c[0] for c in t['comment_before'])
        init_dict['comment'] = comment
    return Project(**init_dict)


project.setParseAction(parse_project)
