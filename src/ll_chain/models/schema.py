from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class NodeContext:
    files: list[str] = field(default_factory=list)


@dataclass
class Node:
    id: str
    prompt: str
    depends_on: list[str] = field(default_factory=list)
    context: NodeContext | None = None


@dataclass
class Schema:
    id: str
    description: str = ""
    nodes: list[Node] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Schema:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if "id" not in data:
            raise ValueError(f"Schema 缺少必需字段 'id': {path}")
        if "nodes" not in data or not data["nodes"]:
            raise ValueError(f"Schema 缺少必需字段 'nodes': {path}")
        nodes = []
        for n in data["nodes"]:
            ctx = None
            if "context" in n:
                ctx = NodeContext(files=n["context"].get("files", []))
            nodes.append(
                Node(
                    id=n["id"],
                    prompt=n.get("prompt", ""),
                    depends_on=n.get("depends_on", []),
                    context=ctx,
                )
            )
        return cls(
            id=data["id"],
            description=data.get("description", ""),
            nodes=nodes,
        )

    def get_node(self, node_id: str) -> Node | None:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None