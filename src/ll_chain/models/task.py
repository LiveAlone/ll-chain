from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml


@dataclass
class StageState:
    status: str = "pending"
    started_at: str | None = None
    completed_at: str | None = None

    def to_dict(self) -> dict:
        d: dict = {"status": self.status}
        if self.started_at is not None:
            d["started_at"] = self.started_at
        if self.completed_at is not None:
            d["completed_at"] = self.completed_at
        return d

    @classmethod
    def from_dict(cls, data: dict) -> StageState:
        return cls(
            status=data.get("status", "pending"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )


@dataclass
class Task:
    name: str
    flow: str
    status: str = "pending"
    created_at: str = ""
    instruction: str | None = None
    stages: dict[str, StageState] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> Task:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        stages = {}
        for sid, sdata in (data.get("stages") or {}).items():
            stages[sid] = StageState.from_dict(sdata)
        return cls(
            name=data["name"],
            flow=data["flow"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at", ""),
            instruction=data.get("instruction"),
            stages=stages,
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.to_dict(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                indent=2,
                sort_keys=False,
            )

    def to_dict(self) -> dict:
        d: dict = {
            "name": self.name,
            "flow": self.flow,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.instruction is not None:
            d["instruction"] = self.instruction
        d["stages"] = {sid: s.to_dict() for sid, s in self.stages.items()}
        return d

    @classmethod
    def create(
        cls,
        name: str,
        flow: str,
        node_ids: list[str],
        instruction: str | None = None,
    ) -> Task:
        now = datetime.now().isoformat(timespec="seconds")
        stages = {nid: StageState() for nid in node_ids}
        return cls(
            name=name,
            flow=flow,
            status="pending",
            created_at=now,
            instruction=instruction,
            stages=stages,
        )