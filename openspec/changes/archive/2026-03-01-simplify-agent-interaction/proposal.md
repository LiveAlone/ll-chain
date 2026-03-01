## Why

当前 ll-chain 使用三层架构（CLI → MainAgent → SubAgent/Worker），SubAgent 交互增加了不必要的复杂度。MainAgent 需要通过 `Task(SubAgent)` 派发 Worker 执行每个 stage，整个流水线在一次 `/ll-run` 中自动跑完，用户对中间过程无感知。简化为用户手动驱动的 human-in-the-loop 模型，降低复杂度，同时让用户能在每轮 DAG 执行后审查结果再决定是否继续。

## What Changes

- **BREAKING** 删除 `/ll-worker` Skill — 不再需要独立的 Worker 执行协议
- **BREAKING** 重写 `/ll-run` Skill — 从"自动编排循环 + 派发 SubAgent"变为"执行当前轮所有 ready stages + 引导用户手动触发下一轮"
- 融合 Worker 的 stage 执行逻辑（QUERY → LOAD CONTEXT → EXECUTE → OUTPUT）到 `/ll-run` 内部
- `init` 命令不再注入 `ll-worker.md` 到 `.claude/commands/`
- `/ll-create` Skill 不变
- CLI 命令（`status`, `stage`, `update` 等）不变

## Capabilities

### New Capabilities

- `ll-run-skill`: `/ll-run` Skill 的新执行协议 — 查状态、顺序执行当前轮 ready stages、加载两层 Context、输出结果、引导用户下一步

### Modified Capabilities

（无已有 specs）

## Impact

- **Skill 模板文件**:
  - `src/ll_chain/templates/ll-run.md` — 重写
  - `src/ll_chain/templates/ll-worker.md` — 删除
- **CLI 代码**:
  - `src/ll_chain/commands/init_cmd.py` — 移除 `ll-worker.md` 的注入逻辑
- **设计文档**:
  - `docs/design.md` — 已更新（三层分工→两层分工、用户驱动模型等）
- **CLAUDE.md** — 需同步更新架构描述（三层→两层、移除 Worker 相关说明）
- **用户影响**: 使用旧版 `/ll-worker` 和 `/ll-run` 的用户需重新执行 `ll-chain init` 更新 Skills
