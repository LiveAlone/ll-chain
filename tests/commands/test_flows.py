import json

from click.testing import CliRunner

from ll_chain.commands.flows import flows_cmd
from ll_chain.utils.yaml_io import save_yaml


def _setup(tmp_path, monkeypatch, *, schemas=None, default_flow=None):
    monkeypatch.chdir(tmp_path)
    llchain_dir = tmp_path / ".llchain"
    monkeypatch.setattr("ll_chain.commands.flows.LLCHAIN_DIR", llchain_dir)

    llchain_dir.mkdir()
    (llchain_dir / "schemas").mkdir()

    config_data = {"constraints": []}
    if default_flow is not None:
        config_data["default_flow_id"] = default_flow
    save_yaml(llchain_dir / "config.yaml", config_data)

    for s in (schemas or []):
        save_yaml(llchain_dir / "schemas" / f"{s['id']}.yaml", s)

    return llchain_dir


class TestFlowsCommand:
    def test_list_flows(self, tmp_path, monkeypatch):
        _setup(tmp_path, monkeypatch, schemas=[
            {"id": "code-review", "description": "代码审查", "nodes": [{"id": "a", "prompt": "p"}]},
            {"id": "refactor", "description": "重构", "nodes": [{"id": "b", "prompt": "p"}]},
        ])
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["flows"]) == 2
        ids = [f["id"] for f in data["flows"]]
        assert "code-review" in ids
        assert "refactor" in ids

    def test_empty_schemas(self, tmp_path, monkeypatch):
        _setup(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["flows"] == []

    def test_with_default_flow(self, tmp_path, monkeypatch):
        _setup(tmp_path, monkeypatch, default_flow="code-review")
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["default_flow"] == "code-review"

    def test_without_default_flow(self, tmp_path, monkeypatch):
        _setup(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["default_flow"] is None

    def test_not_initialized(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.flows.LLCHAIN_DIR", tmp_path / ".llchain")

        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code != 0
        assert "尚未初始化" in result.output