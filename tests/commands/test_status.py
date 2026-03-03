import json

from click.testing import CliRunner

from ll_chain.commands.status import status_cmd
from ll_chain.utils.yaml_io import save_yaml


def _setup(tmp_path, monkeypatch, *, instruction=None):
    monkeypatch.chdir(tmp_path)
    llchain_dir = tmp_path / ".llchain"
    monkeypatch.setattr("ll_chain.commands.status.LLCHAIN_DIR", llchain_dir)

    llchain_dir.mkdir()
    (llchain_dir / "schemas").mkdir()

    schema_data = {
        "id": "test-flow",
        "description": "测试流程",
        "nodes": [
            {"id": "step1", "prompt": "执行步骤一"},
            {"id": "step2", "prompt": "执行步骤二", "depends_on": ["step1"]},
        ],
    }
    save_yaml(llchain_dir / "schemas" / "test-flow.yaml", schema_data)

    task_data = {
        "name": "my-task",
        "flow": "test-flow",
        "status": "pending",
        "created_at": "2026-01-01T00:00:00",
        "stages": {
            "step1": {"status": "pending"},
            "step2": {"status": "pending"},
        },
    }
    if instruction is not None:
        task_data["instruction"] = instruction

    task_dir = llchain_dir / "my-task"
    task_dir.mkdir()
    save_yaml(task_dir / "task.yaml", task_data)

    return llchain_dir


class TestStatusInstruction:
    def test_with_instruction(self, tmp_path, monkeypatch):
        """task 有 instruction 时输出中包含该字段"""
        _setup(tmp_path, monkeypatch, instruction="重点关注安全性")
        runner = CliRunner()
        result = runner.invoke(status_cmd, ["my-task", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["instruction"] == "重点关注安全性"

    def test_without_instruction(self, tmp_path, monkeypatch):
        """task 无 instruction 时输出中不包含该字段"""
        _setup(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(status_cmd, ["my-task", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "instruction" not in data
