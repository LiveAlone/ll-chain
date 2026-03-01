import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.core.context import build_stage_context
from ll_chain.models.config import Config
from ll_chain.models.schema import Schema
from ll_chain.models.task import Task
from ll_chain.utils.output import output_result


@click.command()
@click.argument("task_name")
@click.argument("node_id")
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def stage_cmd(task_name: str, node_id: str, as_json: bool):
    """查询 stage 详情（两层 Context）"""
    if not LLCHAIN_DIR.exists():
        raise click.ClickException("尚未初始化，请先执行 ll-chain init")

    task_file = LLCHAIN_DIR / task_name / "task.yaml"
    if not task_file.exists():
        raise click.ClickException(f"Task 不存在：{task_name}")

    task = Task.load(task_file)
    schema = Schema.load(LLCHAIN_DIR / "schemas" / f"{task.flow}.yaml")
    config = Config.load(LLCHAIN_DIR / "config.yaml")

    try:
        result = build_stage_context(task, schema, config, node_id, LLCHAIN_DIR)
    except ValueError as e:
        raise click.ClickException(str(e))

    output_result(result, as_json)