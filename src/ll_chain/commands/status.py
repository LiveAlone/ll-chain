import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.core.dag import compute_ready_stages
from ll_chain.core.schema_resolver import resolve_schema_path
from ll_chain.models.schema import Schema
from ll_chain.models.task import Task
from ll_chain.utils.output import output_result


@click.command()
@click.argument("task_name")
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def status_cmd(task_name: str, as_json: bool):
    """查询 task 状态"""
    if not LLCHAIN_DIR.exists():
        raise click.ClickException("尚未初始化，请先执行 ll-chain init")

    task_file = LLCHAIN_DIR / task_name / "task.yaml"
    if not task_file.exists():
        raise click.ClickException(f"Task 不存在：{task_name}")

    task = Task.load(task_file)
    schema = Schema.load(resolve_schema_path(task.flow))
    ready = compute_ready_stages(schema.nodes, task.stages)

    result = {
        "name": task.name,
        "flow": task.flow,
        "status": task.status,
        "ready_stages": ready,
        "completed_stages": [s for s, st in task.stages.items() if st.status == "completed"],
        "failed_stages": [s for s, st in task.stages.items() if st.status == "failed"],
    }

    if task.instruction is not None:
        result["instruction"] = task.instruction

    output_result(result, as_json)