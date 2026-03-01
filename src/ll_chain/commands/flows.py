import click

from ll_chain.constants import LLCHAIN_DIR
from ll_chain.models.config import Config
from ll_chain.models.schema import Schema
from ll_chain.utils.output import output_result


@click.command()
@click.option("--json", "as_json", is_flag=True, help="以 JSON 格式输出")
def flows_cmd(as_json: bool):
    """列出可用的 flow schemas"""
    if not LLCHAIN_DIR.exists():
        raise click.ClickException("尚未初始化，请先执行 ll-chain init")

    schemas_dir = LLCHAIN_DIR / "schemas"
    flows = []
    for path in sorted(schemas_dir.glob("*.yaml")):
        schema = Schema.load(path)
        flows.append({"id": schema.id, "description": schema.description})

    config = Config.load(LLCHAIN_DIR / "config.yaml")

    output_result({
        "flows": flows,
        "default_flow": config.default_flow_id,
    }, as_json)