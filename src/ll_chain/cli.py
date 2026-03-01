import click

from ll_chain.commands.init_cmd import init_cmd
from ll_chain.commands.create import create_cmd
from ll_chain.commands.list_cmd import list_cmd
from ll_chain.commands.status import status_cmd
from ll_chain.commands.stage import stage_cmd
from ll_chain.commands.update import update_cmd
from ll_chain.commands.flows import flows_cmd


@click.group()
def cli():
    """ll-chain — AI 工作流编排工具"""
    pass


cli.add_command(init_cmd, "init")
cli.add_command(create_cmd, "create")
cli.add_command(list_cmd, "list")
cli.add_command(status_cmd, "status")
cli.add_command(stage_cmd, "stage")
cli.add_command(update_cmd, "update")
cli.add_command(flows_cmd, "flows")