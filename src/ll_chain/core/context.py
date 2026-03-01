from __future__ import annotations

from pathlib import Path

from ll_chain.models.config import Config
from ll_chain.models.schema import Schema
from ll_chain.models.task import Task


def build_stage_context(
    task: Task,
    schema: Schema,
    config: Config,
    node_id: str,
    llchain_dir: Path,
) -> dict:
    node = schema.get_node(node_id)
    if node is None:
        raise ValueError(f"节点 '{node_id}' 在 flow '{schema.id}' 中不存在")

    stage = task.stages.get(node_id)
    if stage is None:
        raise ValueError(f"Stage '{node_id}' 在 task '{task.name}' 中不存在")

    task_dir = llchain_dir / task.name

    # Layer 1: constraints (仅来自 config)
    constraints = list(config.constraints)

    # Layer 2: dependencies
    dependencies = []
    for dep_id in node.depends_on:
        dep_dir = task_dir / f"stage-{dep_id}"
        dependencies.append({
            "node": dep_id,
            "summary": str(dep_dir / "summary.md"),
            "output_dir": str(dep_dir) + "/",
        })

    output_dir = task_dir / f"stage-{node_id}"

    # instruction: prompts 列表
    prompts: list[dict] = [{"source": "schema", "content": node.prompt}]
    if not node.depends_on and task.instruction:
        prompts.append({"source": "user", "content": task.instruction})

    return {
        "node": node_id,
        "task": task.name,
        "status": stage.status,
        "instruction": {"prompts": prompts},
        "constraints": constraints,
        "dependencies": dependencies,
        "output_dir": str(output_dir) + "/",
    }