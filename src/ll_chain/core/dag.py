from __future__ import annotations

from ll_chain.models.schema import Node
from ll_chain.models.task import StageState


def validate_dag(nodes: list[Node]) -> None:
    node_ids = {n.id for n in nodes}

    # 检查 depends_on 引用合法性
    for n in nodes:
        for dep in n.depends_on:
            if dep not in node_ids:
                raise ValueError(
                    f"节点 '{n.id}' 依赖的节点 '{dep}' 不存在"
                )

    # 拓扑排序检测环
    in_degree: dict[str, int] = {n.id: 0 for n in nodes}
    adj: dict[str, list[str]] = {n.id: [] for n in nodes}
    for n in nodes:
        for dep in n.depends_on:
            adj[dep].append(n.id)
            in_degree[n.id] += 1

    queue = [nid for nid, d in in_degree.items() if d == 0]
    visited = 0
    while queue:
        nid = queue.pop(0)
        visited += 1
        for child in adj[nid]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if visited != len(nodes):
        raise ValueError("DAG 中存在循环依赖")


def compute_ready_stages(
    nodes: list[Node],
    stages: dict[str, StageState],
) -> list[str]:
    ready = []
    for n in nodes:
        stage = stages.get(n.id)
        if stage is None or stage.status != "pending":
            continue
        deps_met = all(
            stages.get(dep) is not None and stages[dep].status == "completed"
            for dep in n.depends_on
        )
        if deps_met:
            ready.append(n.id)
    return ready


def derive_task_status(stages: dict[str, StageState]) -> str:
    statuses = [s.status for s in stages.values()]
    if any(s == "failed" for s in statuses):
        return "failed"
    if any(s == "running" for s in statuses):
        return "running"
    if all(s == "completed" for s in statuses):
        return "completed"
    return "pending"