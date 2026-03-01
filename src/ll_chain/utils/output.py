from __future__ import annotations

import json

import click

from ll_chain.utils.yaml_io import dump_yaml


pass_json = click.make_pass_decorator(bool, ensure=True)


def output_result(data: dict, as_json: bool) -> None:
    if as_json:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        click.echo(dump_yaml(data))