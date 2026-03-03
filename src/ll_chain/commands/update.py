from datetime import datetime

import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.core.dag import derive_task_status
from ll_chain.models.task import Task
from ll_chain.utils.output import output_result

VALID_STATUSES = ("pending", "completed", "failed")


@click.command()
@click.argument("task_name")
@click.argument("node_id")
@click.argument("status")
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def update_cmd(task_name: str, node_id: str, status: str, as_json: bool):
    """更新 stage 状态"""
    if not LLCHAIN_DIR.exists():
        raise click.ClickException("尚未初始化，请先执行 ll-chain init")

    if status not in VALID_STATUSES:
        raise click.ClickException(
            f"无效状态值：'{status}'，有效值为 {VALID_STATUSES}"
        )

    task_file = LLCHAIN_DIR / task_name / "task.yaml"
    if not task_file.exists():
        raise click.ClickException(f"Task 不存在：{task_name}")

    task = Task.load(task_file)

    if node_id not in task.stages:
        raise click.ClickException(
            f"Stage '{node_id}' 在 task '{task_name}' 中不存在"
        )

    stage = task.stages[node_id]
    now = datetime.now().isoformat(timespec="seconds")

    stage.status = status
    if status in ("completed", "failed"):
        stage.completed_at = now
    elif status == "pending":
        stage.completed_at = None

    task.status = derive_task_status(task.stages)
    task.save(task_file)

    output_result({
        "task": task_name,
        "node": node_id,
        "stage_status": status,
        "task_status": task.status,
    }, as_json)