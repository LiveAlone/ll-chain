## Why

当前 stage 状态模型有 4 种状态（`pending | running | failed | completed`），其中 `running` 状态引入了不必要的复杂性：Agent 执行 stage 前需先 `update running`，执行后再 `update completed/failed`，形成两步操作。如果 Agent 被中断（用户中止、上下文溢出等），stage 会停留在 `running` 状态，无法被 `compute_ready_stages` 重新拾起，导致 task 卡死。去除 `running` 状态可以简化流程，并天然支持中断后重复执行。

## What Changes

- **BREAKING** 移除 `running` 状态值，stage 状态简化为 `pending | completed | failed`
- **BREAKING** `update` 命令不再接受 `running` 作为有效状态值
- `compute_ready_stages` 调整：`pending` 的 stage 在依赖满足时即为 ready，与当前行为一致
- `derive_task_status` 移除 `running` 分支：不再有 task 级别的 `running` 状态
- `StageState` 移除 `started_at` 字段（不再需要标记开始时间）
- `ll-run` 模板更新：执行 stage 时跳过 `update running` 步骤，直接查询 context 并执行
- `status` 命令输出移除 `running_stages` 字段
- 允许对 `failed` 的 stage 重新设置为 `pending` 以支持重试

## Capabilities

### New Capabilities

- `stage-retry`: 支持将 `failed` 状态的 stage 重置为 `pending`，允许重试执行

### Modified Capabilities

（无需修改现有 spec 级别的能力，此变更属于状态模型的内部简化）

## Impact

- **代码文件**：`models/task.py`（StageState）、`core/dag.py`（compute_ready_stages, derive_task_status）、`commands/update.py`、`commands/status.py`
- **模板文件**：`templates/ll-run.md`（执行协议步骤调整）、`templates/ll-create.md`（如涉及状态说明）
- **架构文档**：`docs/design.md` — 更新 §5.3 状态流转、§6.4 Task 数据模型示例、§9 执行协议、§10 Agent 交互流程中所有涉及 `running` 状态的描述和示例
- **测试文件**：`tests/core/test_dag.py`、`tests/core/test_context_prompts.py` 中涉及 `running` 状态的用例
- **向后兼容**：破坏性变更。现有 `running` 状态的 task.yaml 文件将不被识别，需手动修复或重新创建