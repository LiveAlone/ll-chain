import json
from pathlib import Path

import yaml
from click.testing import CliRunner

from ll_chain.commands.init_cmd import init_cmd
from ll_chain.models.schema import Schema


class TestInitSchemaInjection:
    def test_first_init_copies_demo_schema(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        runner = CliRunner()
        result = runner.invoke(init_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "code-review.yaml" in data["schemas_injected"]
        assert data["schemas_skipped"] == []

        # 验证文件存在且可被 Schema.load() 加载
        schema_path = tmp_path / ".llchain" / "schemas" / "code-review.yaml"
        assert schema_path.exists()
        schema = Schema.load(schema_path)
        assert schema.id == "code-review"
        assert len(schema.nodes) == 3

    def test_existing_schema_is_skipped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        # 预先创建 schema 文件
        schemas_dir = tmp_path / ".llchain" / "schemas"
        schemas_dir.mkdir(parents=True)
        (schemas_dir / "code-review.yaml").write_text("id: custom\nnodes:\n  - id: x\n    prompt: test\n")

        # 需要先删除 .llchain 让 init 能跑，但 schemas 已有文件
        # 实际上 init 会检查 .llchain 存在就报错，所以这里需要换个方式
        # 直接测试 _inject_schemas 函数
        from ll_chain.commands.init_cmd import _inject_schemas
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        injected, skipped = _inject_schemas()
        assert "code-review.yaml" in skipped
        assert injected == []

        # 原有内容未被覆盖
        assert "custom" in (schemas_dir / "code-review.yaml").read_text()


class TestInitDefaultFlowId:
    def test_config_has_default_flow_id(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        runner = CliRunner()
        result = runner.invoke(init_cmd, ["--json"])

        assert result.exit_code == 0
        config_path = tmp_path / ".llchain" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config["default_flow_id"] == "code-review"


class TestInitSkillsInjection:
    def test_first_init_injects_skills(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        runner = CliRunner()
        result = runner.invoke(init_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "ll-run.md" in data["skills_injected"]
        assert "ll-create.md" in data["skills_injected"]
        assert data["skills_skipped"] == []

        # 验证文件确实被复制
        commands_dir = tmp_path / ".claude" / "commands"
        assert (commands_dir / "ll-run.md").exists()
        assert (commands_dir / "ll-create.md").exists()
        assert not (commands_dir / "ll-worker.md").exists()

        # 验证文件内容非空
        assert (commands_dir / "ll-run.md").read_text().strip()
        assert (commands_dir / "ll-create.md").read_text().strip()

    def test_existing_skills_are_skipped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        # 预先创建一个 skill 文件
        commands_dir = tmp_path / ".claude" / "commands"
        commands_dir.mkdir(parents=True)
        (commands_dir / "ll-run.md").write_text("custom content")

        runner = CliRunner()
        result = runner.invoke(init_cmd, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "ll-run.md" in data["skills_skipped"]
        assert "ll-create.md" in data["skills_injected"]

        # 已存在的文件内容不被覆盖
        assert (commands_dir / "ll-run.md").read_text() == "custom content"

    def test_init_creates_llchain_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")

        runner = CliRunner()
        result = runner.invoke(init_cmd, ["--json"])

        assert result.exit_code == 0
        assert (tmp_path / ".llchain").exists()
        assert (tmp_path / ".llchain" / "schemas").exists()
        assert (tmp_path / ".llchain" / "config.yaml").exists()

    def test_init_fails_if_already_initialized(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ll_chain.commands.init_cmd.LLCHAIN_DIR", tmp_path / ".llchain")
        (tmp_path / ".llchain").mkdir()

        runner = CliRunner()
        result = runner.invoke(init_cmd, ["--json"])

        assert result.exit_code != 0
        assert "已初始化" in result.output