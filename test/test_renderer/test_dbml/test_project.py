from pydbml.classes import Project, Note
from pydbml.renderer.dbml.default.project import render_items, render_project


class TestRenderItems:
    @staticmethod
    def test_oneline():
        project = Project(name="test", items={"key1": "value1"})
        assert render_items(project.items) == "    key1: 'value1'\n"

    @staticmethod
    def test_multiline():
        project = Project(name="test", items={"key1": "value1\nvalue2"})
        assert render_items(project.items) == "    key1: '''value1\n    value2'''\n"

    @staticmethod
    def test_multiple():
        project = Project(
            name="test", items={"key1": "value1", "key2": "value2\nnewline"}
        )
        assert (
            render_items(project.items)
            == "    key1: 'value1'\n    key2: '''value2\n    newline'''\n"
        )


class TestRenderProject:
    @staticmethod
    def test_no_note() -> None:
        project = Project(name="test", items={"key1": "value1"})
        expected = "Project \"test\" {\n    key1: 'value1'\n}"
        assert render_project(project) == expected

    @staticmethod
    def test_note() -> None:
        project = Project(name="test", items={"key1": "value1"})
        project.note = Note("Note text")
        expected = (
            'Project "test" {\n'
            "    key1: 'value1'\n"
            "    Note {\n"
            "        'Note text'\n"
            "    }\n"
            "}"
        )
        assert render_project(project) == expected
