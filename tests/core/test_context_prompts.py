from pathlib import Path

from ll_chain.core.context import build_stage_context
from ll_chain.models.config import Config
from ll_chain.models.schema import Node, Schema
from ll_chain.models.task import StageState, Task


def _make_schema() -> Schema:
    return Schema(
        id="review",
        description="test",
        nodes=[
            Node(id="analyze", prompt="分析代码"),
            Node(id="security", prompt="安全审查"),
            Node(id="report", prompt="生成报告", depends_on=["analyze", "security"]),
        ],
    )


def _make_task(instruction: str | None = None) -> Task:
    return Task(
        name="t",
        flow="review",
        status="pending",
        created_at="2026-01-01T00:00:00",
        instruction=instruction,
        stages={
            "analyze": StageState(status="completed"),
            "security": StageState(status="completed"),
            "report": StageState(status="pending"),
        },
    )


class TestContextPrompts:
    def test_entry_node_with_instruction(self, tmp_path: Path):
        schema = _make_schema()
        task = _make_task(instruction="重点关注 auth 模块")
        config = Config(constraints=["中文输出"])

        result = build_stage_context(task, schema, config, "analyze", tmp_path)

        prompts = result["instruction"]["prompts"]
        assert len(prompts) == 2
        assert prompts[0] == {"source": "schema", "content": "分析代码"}
        assert prompts[1] == {"source": "user", "content": "重点关注 auth 模块"}

    def test_entry_node_without_instruction(self, tmp_path: Path):
        schema = _make_schema()
        task = _make_task(instruction=None)
        config = Config()

        result = build_stage_context(task, schema, config, "analyze", tmp_path)

        prompts = result["instruction"]["prompts"]
        assert len(prompts) == 1
        assert prompts[0] == {"source": "schema", "content": "分析代码"}

    def test_non_entry_node_with_instruction(self, tmp_path: Path):
        """非入口节点也注入 user instruction"""
        schema = _make_schema()
        task = _make_task(instruction="重点关注 auth 模块")
        config = Config()

        result = build_stage_context(task, schema, config, "report", tmp_path)

        prompts = result["instruction"]["prompts"]
        assert len(prompts) == 2
        assert prompts[0] == {"source": "schema", "content": "生成报告"}
        assert prompts[1] == {"source": "user", "content": "重点关注 auth 模块"}

    def test_non_entry_node_without_instruction(self, tmp_path: Path):
        schema = _make_schema()
        task = _make_task(instruction=None)
        config = Config()

        result = build_stage_context(task, schema, config, "report", tmp_path)

        prompts = result["instruction"]["prompts"]
        assert len(prompts) == 1
        assert prompts[0] == {"source": "schema", "content": "生成报告"}

    def test_multiple_entry_nodes_all_get_instruction(self, tmp_path: Path):
        """多个入口节点都收到 user instruction"""
        schema = _make_schema()
        task = _make_task(instruction="重点关注 auth 模块")
        config = Config()

        for node_id in ("analyze", "security"):
            result = build_stage_context(task, schema, config, node_id, tmp_path)
            prompts = result["instruction"]["prompts"]
            assert len(prompts) == 2
            assert prompts[1]["source"] == "user"