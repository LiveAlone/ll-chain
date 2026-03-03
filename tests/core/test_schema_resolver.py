import pytest
from pathlib import Path
from unittest.mock import patch

import click

from ll_chain.core.schema_resolver import resolve_schema_path, load_all_schemas


# ── resolve_schema_path ──


class TestResolveSchemaPath:
    def test_project_dir_only(self, tmp_path):
        project_schemas = tmp_path / ".llchain" / "schemas"
        project_schemas.mkdir(parents=True)
        (project_schemas / "my-flow.yaml").write_text("id: my-flow\ndescription: test\nnodes: []")

        with patch("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain"), \
             patch("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", tmp_path / "nonexistent"):
            result = resolve_schema_path("my-flow")
            assert result == project_schemas / "my-flow.yaml"

    def test_user_dir_only(self, tmp_path):
        user_schemas = tmp_path / "user-schemas"
        user_schemas.mkdir(parents=True)
        (user_schemas / "my-flow.yaml").write_text("id: my-flow\ndescription: test\nnodes: []")

        project_schemas = tmp_path / ".llchain" / "schemas"
        project_schemas.mkdir(parents=True)

        with patch("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain"), \
             patch("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", user_schemas):
            result = resolve_schema_path("my-flow")
            assert result == user_schemas / "my-flow.yaml"

    def test_both_dirs_project_wins(self, tmp_path):
        project_schemas = tmp_path / ".llchain" / "schemas"
        project_schemas.mkdir(parents=True)
        (project_schemas / "my-flow.yaml").write_text("id: my-flow\ndescription: project\nnodes: []")

        user_schemas = tmp_path / "user-schemas"
        user_schemas.mkdir(parents=True)
        (user_schemas / "my-flow.yaml").write_text("id: my-flow\ndescription: user\nnodes: []")

        with patch("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain"), \
             patch("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", user_schemas):
            result = resolve_schema_path("my-flow")
            assert result == project_schemas / "my-flow.yaml"

    def test_not_found(self, tmp_path):
        project_schemas = tmp_path / ".llchain" / "schemas"
        project_schemas.mkdir(parents=True)

        with patch("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain"), \
             patch("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", tmp_path / "nonexistent"):
            with pytest.raises(click.ClickException, match="Schema 不存在"):
                resolve_schema_path("no-such-flow")


# ── load_all_schemas ──


class TestLoadAllSchemas:
    def _write_schema(self, directory: Path, schema_id: str, description: str):
        directory.mkdir(parents=True, exist_ok=True)
        content = (
            f"id: {schema_id}\n"
            f"description: {description}\n"
            "nodes:\n"
            "  - id: start\n"
            "    prompt: placeholder\n"
        )
        (directory / f"{schema_id}.yaml").write_text(content)

    def test_merge_both_dirs(self, tmp_path):
        project_schemas = tmp_path / ".llchain" / "schemas"
        user_schemas = tmp_path / "user-schemas"

        self._write_schema(user_schemas, "a", "user-a")
        self._write_schema(user_schemas, "b", "user-b")
        self._write_schema(project_schemas, "b", "project-b")
        self._write_schema(project_schemas, "c", "project-c")

        with patch("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain"), \
             patch("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", user_schemas):
            schemas = load_all_schemas()

        assert set(schemas.keys()) == {"a", "b", "c"}
        assert schemas["a"].description == "user-a"
        assert schemas["b"].description == "project-b"  # 项目覆盖
        assert schemas["c"].description == "project-c"

    def test_user_dir_not_exists(self, tmp_path):
        project_schemas = tmp_path / ".llchain" / "schemas"
        self._write_schema(project_schemas, "x", "project-x")

        with patch("ll_chain.core.schema_resolver.LLCHAIN_DIR", tmp_path / ".llchain"), \
             patch("ll_chain.core.schema_resolver.USER_SCHEMAS_DIR", tmp_path / "nonexistent"):
            schemas = load_all_schemas()

        assert set(schemas.keys()) == {"x"}
        assert schemas["x"].description == "project-x"
