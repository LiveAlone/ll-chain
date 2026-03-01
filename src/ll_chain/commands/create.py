import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.core.dag import validate_dag
from ll_chain.models.schema import Schema
from ll_chain.models.task import Task
from ll_chain.utils.output import output_result


@click.command()
@click.argument("task_name")
@click.option("--flow", required=True, help="Flow schema ID")
@click.option("--instruction", default=None, help="用户业务说明（注入到入口节点）")
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def create_cmd(task_name: str, flow: str, instruction: str | None, as_json: bool):
    """从 flow 创建 task 实例"""
    if not LLCHAIN_DIR.exists():
        raise click.ClickException("尚未初始化，请先执行 ll-chain init")

    schema_path = LLCHAIN_DIR / "schemas" / f"{flow}.yaml"
    if not schema_path.exists():
        raise click.ClickException(f"Schema 不存在：{schema_path}")

    task_dir = LLCHAIN_DIR / task_name
    if task_dir.exists():
        raise click.ClickException(f"Task 已存在：{task_name}")

    schema = Schema.load(schema_path)
    validate_dag(schema.nodes)

    node_ids = [n.id for n in schema.nodes]
    task = Task.create(name=task_name, flow=flow, node_ids=node_ids, instruction=instruction)
    task_dir.mkdir(parents=True)
    task.save(task_dir / "task.yaml")

    output_result({"message": f"已创建 task '{task_name}'（flow: {flow}）"}, as_json)