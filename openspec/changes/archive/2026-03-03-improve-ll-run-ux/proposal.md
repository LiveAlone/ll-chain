## Why

`ll-run` skill 当前要求用户必须手动传入 task 名称（`/ll-run <task_name>`），这在只有一个 task 时是多余操作，增加使用摩擦。此外 `summary.md` 输出过于自由，缺乏结构约束，导致下游节点难以高效消费上游输出。

## What Changes

- **自动推断 task**：当用户不传入 task 参数时，自动通过 `ll-chain list` 查询。若仅有一个 task 则自动选用；若无 task 则引导用户创建；若多个 task 则列出供用户选择。
- **精简 summary.md 规范**：将 `summary.md` 的定位明确为 `output_dir` 的元信息索引，仅列出目录中每个文件及其功能说明，不包含额外内容。

## Capabilities

### New Capabilities

- `auto-task-resolve`: 自动推断当前 task 的逻辑，当 `$ARGUMENTS` 为空时通过 list 查询并智能选择或引导用户
- `summary-format`: 规范 summary.md 的输出格式为 output_dir 文件索引

### Modified Capabilities

（无现有 spec 需修改）

## Impact

- **模板文件**：`src/ll_chain/templates/ll-run.md` — 需修改 skill 模板内容
- **无代码变更**：此改动仅涉及 skill 模板（prompt 文件），不涉及 Python 代码或 CLI 逻辑
