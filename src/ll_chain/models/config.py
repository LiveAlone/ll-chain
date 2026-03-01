from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    constraints: list[str] = field(default_factory=list)
    default_flow_id: str | None = None

    @classmethod
    def load(cls, path: Path) -> Config:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(
            constraints=data.get("constraints", []),
            default_flow_id=data.get("default_flow_id"),
        )

    def to_dict(self) -> dict:
        result: dict = {"constraints": self.constraints}
        if self.default_flow_id is not None:
            result["default_flow_id"] = self.default_flow_id
        return result