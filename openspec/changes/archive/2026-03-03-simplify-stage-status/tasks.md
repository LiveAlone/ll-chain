## 1. 数据模型与核心逻辑

- [x] 1.1 修改 `StageState`（`models/task.py`）：移除 `started_at` 字段，更新 `to_dict()` 和 `from_dict()` 方法
- [x] 1.2 修改 `derive_task_status`（`core/dag.py`）：移除 `running` 分支，仅保留 `failed / completed / pending` 三态推导
- [x] 1.3 修改 `compute_ready_stages`（`core/dag.py`）：确认逻辑无需改动（已仅检查 `pending`），添加注释说明

## 2. 命令层修改

- [x] 2.1 修改 `update` 命令（`commands/update.py`）：`VALID_STATUSES` 改为 `("pending", "completed", "failed")`，移除 `running` 分支的时间戳逻辑，`pending` 状态时清除 `completed_at`
- [x] 2.2 修改 `status` 命令（`commands/status.py`）：移除 `running_stages` 字段输出

## 3. 模板与文档

- [x] 3.1 更新 `templates/ll-run.md`：移除步骤 2a 中 `update running` 调用，执行 stage 时直接查询 context 并执行
- [x] 3.2 更新 `docs/design.md`：修改 §5.3 状态流转图（三态）、§6.4 task.yaml 示例（移除 `running` 和 `started_at`）、§9 执行协议（移除 `update running` 步骤）、§10 交互流程（移除所有 `update running` 调用）

## 4. 测试更新

- [x] 4.1 更新 `tests/core/test_dag.py`：移除 `running` 相关测试用例，新增 `failed → pending` 重置后 task 状态推导测试
- [x] 4.2 更新 `tests/core/test_context_prompts.py`：将 `status="running"` 改为有效的三态值
- [x] 4.3 运行全量测试 `uv run pytest` 确认无回归
