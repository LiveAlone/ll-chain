import json

from click.testing import CliRunner

from ll_chain.commands.flows import flows_cmd
from ll_chain.utils.yaml_io import save_yaml


def _setup(tmp_path, monkeypatch, *, schemas=None, default_flow=None, user_schemas=None):
    monkeypatch.chdir(tmp_path)
    llchain_dir = tmp_path / ".llchain"
    monkeypatch.setattr("ll_chain.commands.flows.LLCHAIN_DIR", llchain_dir)
    monkeypatch.setattr("ll_chain.core.schema_resolver.LLCHAIN_DIR", llchain_dir)

    # 用户级 schema 目录
    user_schemas_dir = tmp_path / "user_schemas"
    monkeypatch.setattr("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", user_schemas_dir)

    llchain_dir.mkdir()
    (llchain_dir / "schemas").mkdir()

    config_data = {"constraints": []}
    if default_flow is not None:
        config_data["default_flow_id"] = default_flow
    save_yaml(llchain_dir / "config.yaml", config_data)

    for s in (schemas or []):
        save_yaml(llchain_dir / "schemas" / f"{s['id']}.yaml", s)

    if user_schemas is not None:
        user_schemas_dir.mkdir(parents=True)
        for s in user_schemas:
            save_yaml(user_schemas_dir / f"{s['id']}.yaml", s)

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
        monkeypatch.setattr("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain")
        monkeypatch.setattr("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", tmp_path / "user_schemas")

        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code != 0
        assert "尚未初始化" in result.output

    def test_user_schemas_only(self, tmp_path, monkeypatch):
        """仅用户级目录有 schema"""
        _setup(tmp_path, monkeypatch, user_schemas=[
            {"id": "user-flow", "description": "用户级流程", "nodes": [{"id": "a", "prompt": "p"}]},
        ])
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["flows"]) == 1
        assert data["flows"][0]["id"] == "user-flow"

    def test_project_overrides_user(self, tmp_path, monkeypatch):
        """同名 schema 项目级覆盖用户级"""
        _setup(tmp_path, monkeypatch,
            schemas=[
                {"id": "shared", "description": "项目版本", "nodes": [{"id": "a", "prompt": "p"}]},
            ],
            user_schemas=[
                {"id": "shared", "description": "用户版本", "nodes": [{"id": "b", "prompt": "q"}]},
            ],
        )
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["flows"]) == 1
        assert data["flows"][0]["id"] == "shared"
        assert data["flows"][0]["description"] == "项目版本"

    def test_user_dir_not_exists(self, tmp_path, monkeypatch):
        """用户级目录不存在时正常运行"""
        _setup(tmp_path, monkeypatch, schemas=[
            {"id": "proj-flow", "description": "项目流程", "nodes": [{"id": "a", "prompt": "p"}]},
        ])
        # user_schemas 未传入，所以用户级目录不存在
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["flows"]) == 1
        assert data["flows"][0]["id"] == "proj-flow"

    def test_merge_user_and_project(self, tmp_path, monkeypatch):
        """用户级和项目级不同名 schema 合并展示"""
        _setup(tmp_path, monkeypatch,
            schemas=[
                {"id": "proj-flow", "description": "项目流程", "nodes": [{"id": "a", "prompt": "p"}]},
            ],
            user_schemas=[
                {"id": "user-flow", "description": "用户流程", "nodes": [{"id": "b", "prompt": "q"}]},
            ],
        )
        runner = CliRunner()
        result = runner.invoke(flows_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["flows"]) == 2
        ids = [f["id"] for f in data["flows"]]
        assert "proj-flow" in ids
        assert "user-flow" in ids