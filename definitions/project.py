import pyparsing as pp
from definitions.generic import name, string_literal
from definitions.common import _, note
from classes import Project, Note

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

project_field = pp.Group(name + _ + pp.Suppress(':') + _ + string_literal)

project_element = _ + (note | project_field) + _

project_body = project_element[...]

project = (
    pp.CaselessLiteral('project') + _ +
    name('name') + _ +
    '{' + _ +
    project_body('items') + _ +
    '}'
)


def parse_project(s, l, t):
    init_dict = {'name': t['name']}
    items = {}
    for item in t.get('items', []):
        if isinstance(item, Note):
            init_dict['note'] = item
        else:
            k, v = item
            items[k] = v
    if items:
        init_dict['items': items]
    return Project(**init_dict)


project.setParseAction(parse_project)
