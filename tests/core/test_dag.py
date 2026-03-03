import pytest

from ll_chain.core.dag import compute_ready_stages, derive_task_status, validate_dag
from ll_chain.models.schema import Node
from ll_chain.models.task import StageState


# ── validate_dag ──


class TestValidateDag:
    def test_valid_dag(self):
        nodes = [
            Node(id="a", prompt=""),
            Node(id="b", prompt=""),
            Node(id="c", prompt="", depends_on=["a", "b"]),
        ]
        validate_dag(nodes)  # 不抛异常

    def test_single_node(self):
        nodes = [Node(id="a", prompt="")]
        validate_dag(nodes)

    def test_reference_non_existent_node(self):
        nodes = [Node(id="a", prompt="", depends_on=["non-existent"])]
        with pytest.raises(ValueError, match="不存在"):
            validate_dag(nodes)

    def test_direct_cycle(self):
        nodes = [
            Node(id="a", prompt="", depends_on=["b"]),
            Node(id="b", prompt="", depends_on=["a"]),
        ]
        with pytest.raises(ValueError, match="循环依赖"):
            validate_dag(nodes)

    def test_indirect_cycle(self):
        nodes = [
            Node(id="a", prompt="", depends_on=["c"]),
            Node(id="b", prompt="", depends_on=["a"]),
            Node(id="c", prompt="", depends_on=["b"]),
        ]
        with pytest.raises(ValueError, match="循环依赖"):
            validate_dag(nodes)

    def test_empty_dag(self):
        validate_dag([])


# ── compute_ready_stages ──


class TestComputeReadyStages:
    def test_no_deps_all_ready(self):
        nodes = [
            Node(id="a", prompt=""),
            Node(id="b", prompt=""),
        ]
        stages = {
            "a": StageState(status="pending"),
            "b": StageState(status="pending"),
        }
        assert sorted(compute_ready_stages(nodes, stages)) == ["a", "b"]

    def test_deps_not_completed(self):
        nodes = [
            Node(id="a", prompt=""),
            Node(id="b", prompt=""),
            Node(id="c", prompt="", depends_on=["a", "b"]),
        ]
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="failed"),
            "c": StageState(status="pending"),
        }
        # b is failed so c's deps are not met; b itself is not pending so not ready
        assert compute_ready_stages(nodes, stages) == []

    def test_deps_all_completed(self):
        nodes = [
            Node(id="a", prompt=""),
            Node(id="b", prompt=""),
            Node(id="c", prompt="", depends_on=["a", "b"]),
        ]
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="completed"),
            "c": StageState(status="pending"),
        }
        assert compute_ready_stages(nodes, stages) == ["c"]

    def test_completed_or_failed_not_ready(self):
        nodes = [Node(id="a", prompt="")]
        stages = {"a": StageState(status="completed")}
        assert compute_ready_stages(nodes, stages) == []

        stages = {"a": StageState(status="failed")}
        assert compute_ready_stages(nodes, stages) == []

    def test_dep_has_failed(self):
        nodes = [
            Node(id="a", prompt=""),
            Node(id="b", prompt=""),
            Node(id="c", prompt="", depends_on=["a", "b"]),
        ]
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="failed"),
            "c": StageState(status="pending"),
        }
        assert compute_ready_stages(nodes, stages) == []


# ── derive_task_status ──


class TestDeriveTaskStatus:
    def test_all_pending(self):
        stages = {
            "a": StageState(status="pending"),
            "b": StageState(status="pending"),
        }
        assert derive_task_status(stages) == "pending"

    def test_has_failed(self):
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="failed"),
        }
        assert derive_task_status(stages) == "failed"

    def test_all_completed(self):
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="completed"),
        }
        assert derive_task_status(stages) == "completed"

    def test_mixed_pending_completed(self):
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="pending"),
        }
        assert derive_task_status(stages) == "pending"

    def test_failed_reset_to_pending(self):
        stages = {
            "a": StageState(status="completed"),
            "b": StageState(status="pending"),  # was failed, reset to pending
        }
        assert derive_task_status(stages) == "pending"

    def test_failed_takes_precedence_over_pending(self):
        stages = {
            "a": StageState(status="pending"),
            "b": StageState(status="failed"),
        }
        assert derive_task_status(stages) == "failed"