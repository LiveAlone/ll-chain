import shutil
from pathlib import Path

import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.templates import get_template_path
from ll_chain.utils.output import output_result
from ll_chain.utils.yaml_io import save_yaml

SKILL_FILES = ["ll-run.md", "ll-create.md", "ll-ff.md"]
SCHEMA_FILES = ["code-review.yaml"]


@click.command()
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def init_cmd(as_json: bool):
    """初始化 .llchain/ 目录结构"""
    if LLCHAIN_DIR.exists():
        raise click.ClickException(f"已初始化：{LLCHAIN_DIR} 目录已存在")

    LLCHAIN_DIR.mkdir()
    (LLCHAIN_DIR / "schemas").mkdir()
    save_yaml(LLCHAIN_DIR / "config.yaml", {"constraints": [], "default_flow_id": "code-review"})

    # 注入 demo schema 到 .llchain/schemas/
    schemas_injected, schemas_skipped = _inject_schemas()

    # 注入 Skills 到 .claude/commands/
    injected, skipped = _inject_skills()

    output_result({
        "message": f"已初始化 {LLCHAIN_DIR}/",
        "schemas_injected": schemas_injected,
        "schemas_skipped": schemas_skipped,
        "skills_injected": injected,
        "skills_skipped": skipped,
    }, as_json)


def _inject_schemas() -> tuple[list[str], list[str]]:
    schemas_dir = LLCHAIN_DIR / "schemas"
    injected: list[str] = []
    skipped: list[str] = []

    for name in SCHEMA_FILES:
        dest = schemas_dir / name
        if dest.exists():
            skipped.append(name)
        else:
            src = get_template_path(name)
            shutil.copy2(src, dest)
            injected.append(name)

    return injected, skipped


def _inject_skills() -> tuple[list[str], list[str]]:
    commands_dir = Path(".claude") / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    injected: list[str] = []
    skipped: list[str] = []

    for name in SKILL_FILES:
        dest = commands_dir / name
        if dest.exists():
            skipped.append(name)
        else:
            src = get_template_path(name)
            shutil.copy2(src, dest)
            injected.append(name)

    return injected, skipped
