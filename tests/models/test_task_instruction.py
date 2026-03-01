from pathlib import Path

import yaml

from ll_chain.models.task import Task


class TestTaskInstruction:
    def test_create_with_instruction(self):
        task = Task.create(
            name="t", flow="f", node_ids=["a"], instruction="分析代码"
        )
        assert task.instruction == "分析代码"

    def test_create_without_instruction(self):
        task = Task.create(name="t", flow="f", node_ids=["a"])
        assert task.instruction is None

    def test_to_dict_with_instruction(self):
        task = Task.create(
            name="t", flow="f", node_ids=["a"], instruction="分析代码"
        )
        d = task.to_dict()
        assert d["instruction"] == "分析代码"
        # instruction 在 created_at 之后、stages 之前
        keys = list(d.keys())
        assert keys.index("instruction") < keys.index("stages")

    def test_to_dict_without_instruction(self):
        task = Task.create(name="t", flow="f", node_ids=["a"])
        d = task.to_dict()
        assert "instruction" not in d

    def test_save_and_load_with_instruction(self, tmp_path: Path):
        task = Task.create(
            name="t", flow="f", node_ids=["a"], instruction="分析代码"
        )
        path = tmp_path / "task.yaml"
        task.save(path)

        loaded = Task.load(path)
        assert loaded.instruction == "分析代码"

    def test_save_and_load_without_instruction(self, tmp_path: Path):
        task = Task.create(name="t", flow="f", node_ids=["a"])
        path = tmp_path / "task.yaml"
        task.save(path)

        loaded = Task.load(path)
        assert loaded.instruction is None

    def test_load_old_format_without_instruction(self, tmp_path: Path):
        """旧格式 task.yaml 无 instruction 字段时兼容"""
        path = tmp_path / "task.yaml"
        data = {
            "name": "t",
            "flow": "f",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00",
            "stages": {"a": {"status": "pending"}},
        }
        with open(path, "w") as fh:
            yaml.dump(data, fh)

        loaded = Task.load(path)
        assert loaded.instruction is None