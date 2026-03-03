from pathlib import Path

import click

from ll_chain.constants import LLCHAIN_DIR, USER_SCHEMAS_DIR
from ll_chain.models.schema import Schema


def resolve_schema_path(flow_id: str) -> Path:
    """按优先级查找 schema 文件：项目目录 → 用户目录。"""
    project_path = LLCHAIN_DIR / "schemas" / f"{flow_id}.yaml"
    if project_path.exists():
        return project_path

    user_path = USER_SCHEMAS_DIR / f"{flow_id}.yaml"
    if user_path.exists():
        return user_path

    raise click.ClickException(f"Schema 不存在：{flow_id}")


def load_all_schemas() -> dict[str, Schema]:
    """加载所有 schema，项目目录覆盖用户目录的同 id schema。"""
    schemas: dict[str, Schema] = {}

    # 先加载用户级 schema（低优先级）
    if USER_SCHEMAS_DIR.exists():
        for path in sorted(USER_SCHEMAS_DIR.glob("*.yaml")):
            schema = Schema.load(path)
            schemas[schema.id] = schema

    # 再加载项目级 schema（高优先级，覆盖同 id）
    project_schemas_dir = LLCHAIN_DIR / "schemas"
    if project_schemas_dir.exists():
        for path in sorted(project_schemas_dir.glob("*.yaml")):
            schema = Schema.load(path)
            schemas[schema.id] = schema

    return schemas