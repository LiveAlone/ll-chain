import json

import yaml
from click.testing import CliRunner

from ll_chain.commands.create import create_cmd
from ll_chain.utils.yaml_io import save_yaml


def _setup(tmp_path, monkeypatch):
    """创建 .llchain 目录和一个简单的 schema"""
    monkeypatch.chdir(tmp_path)
    llchain_dir = tmp_path / ".llchain"
    monkeypatch.setattr("ll_chain.commands.create.LLCHAIN_DIR", llchain_dir)

    llchain_dir.mkdir()
    (llchain_dir / "schemas").mkdir()
    save_yaml(llchain_dir / "schemas" / "review.yaml", {
        "id": "review",
        "description": "test",
        "nodes": [
            {"id": "analyze", "prompt": "分析代码"},
            {"id": "report", "prompt": "生成报告", "depends_on": ["analyze"]},
        ],
    })
    return llchain_dir


class TestCreateWithInstruction:
    def test_create_with_instruction(self, tmp_path, monkeypatch):
        llchain_dir = _setup(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(create_cmd, [
            "my-task", "--flow", "review",
            "--instruction", "重点关注 auth 模块",
            "--json",
        ])

        assert result.exit_code == 0
        task_file = llchain_dir / "my-task" / "task.yaml"
        assert task_file.exists()

        with open(task_file) as f:
            data = yaml.safe_load(f)
        assert data["instruction"] == "重点关注 auth 模块"

    def test_create_without_instruction(self, tmp_path, monkeypatch):
        llchain_dir = _setup(tmp_path, monkeypatch)
        runner = CliRunner()
        result = runner.invoke(create_cmd, [
            "my-task", "--flow", "review", "--json",
        ])

        assert result.exit_code == 0
        task_file = llchain_dir / "my-task" / "task.yaml"

        with open(task_file) as f:
            data = yaml.safe_load(f)
        assert "instruction" not in data