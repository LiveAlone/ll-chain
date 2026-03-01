from ll_chain.models.schema import Schema
from ll_chain.templates import get_template_path


class TestGetTemplatePath:
    def test_ll_run_exists(self):
        path = get_template_path("ll-run.md")
        assert path.exists()
        assert path.name == "ll-run.md"

    def test_ll_worker_not_exists(self):
        path = get_template_path("ll-worker.md")
        assert not path.exists()

    def test_nonexistent_template(self):
        path = get_template_path("nonexistent.md")
        assert not path.exists()

    def test_template_content_not_empty(self):
        for name in ("ll-run.md", "ll-create.md"):
            path = get_template_path(name)
            assert path.read_text().strip(), f"{name} should not be empty"


class TestDemoSchema:
    def test_code_review_yaml_exists(self):
        path = get_template_path("code-review.yaml")
        assert path.exists()
        assert path.name == "code-review.yaml"

    def test_schema_load_success(self):
        path = get_template_path("code-review.yaml")
        schema = Schema.load(path)
        assert schema.id == "code-review"
        assert len(schema.nodes) == 3

    def test_node_ids(self):
        path = get_template_path("code-review.yaml")
        schema = Schema.load(path)
        node_ids = [n.id for n in schema.nodes]
        assert node_ids == ["analyze", "security", "report"]

    def test_dag_dependencies(self):
        path = get_template_path("code-review.yaml")
        schema = Schema.load(path)
        analyze = schema.get_node("analyze")
        security = schema.get_node("security")
        report = schema.get_node("report")
        assert analyze.depends_on == []
        assert security.depends_on == []
        assert set(report.depends_on) == {"analyze", "security"}

    def test_nodes_have_prompts(self):
        path = get_template_path("code-review.yaml")
        schema = Schema.load(path)
        for node in schema.nodes:
            assert node.prompt, f"Node {node.id} should have a non-empty prompt"