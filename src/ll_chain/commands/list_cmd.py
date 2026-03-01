import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.models.task import Task
from ll_chain.utils.output import output_result


@click.command()
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def list_cmd(as_json: bool):
    """列出所有 task 实例"""
    if not LLCHAIN_DIR.exists():
        raise click.ClickException("尚未初始化，请先执行 ll-chain init")

    tasks = []
    for d in sorted(LLCHAIN_DIR.iterdir()):
        task_file = d / "task.yaml"
        if d.is_dir() and task_file.exists():
            t = Task.load(task_file)
            tasks.append({"name": t.name, "flow": t.flow, "status": t.status})

    output_result({"tasks": tasks}, as_json)