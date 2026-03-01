from importlib import resources
from pathlib import Path


def get_template_path(name: str) -> Path:
    """定位 templates/ 目录下的模板文件。"""
    ref = resources.files("ll_chain.templates").joinpath(name)
    return Path(str(ref))