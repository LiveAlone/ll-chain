## Context

当前 ll-chain 提供 `/ll-run` skill，每次只执行当前轮次的 ready stages，执行完后提示用户手动调用 `/ll-run` 继续下一轮。对于无需人工介入的流水线场景，需要一个全自动的"快进"模式。

现有模板文件 `ll-run.md` 的步骤 0-2 已经完整定义了 task 确定、状态查询和 stage 执行逻辑。只需在步骤 3 将"引导用户手动触发"替换为"自动循环执行"。

## Goals / Non-Goals

**Goals:**
- 提供 `/ll-ff` skill，实现全自动循环执行 DAG 所有阶段
- 复用 `ll-run.md` 的步骤 0-2 逻辑，保持一致性
- 失败时立即终止，不做自动重试

**Non-Goals:**
- 不修改现有 `ll-run.md` 的行为
- 不修改 ll-chain CLI 的任何命令逻辑
- 不引入新的 CLI 子命令

## Decisions

### 决策 1: 新建独立模板而非参数化现有模板

**选择**: 创建独立的 `ll-ff.md` 模板文件

**理由**: 模板文件是 Markdown 格式的 Agent 指令，不支持条件分支逻辑。将两种行为分成两个文件更清晰，Agent 不需要判断当前是哪种模式。

**替代方案**: 在 `ll-run.md` 中通过参数控制行为 — 但 Markdown 模板不适合做条件逻辑，且会增加 Agent 的理解负担。

### 决策 2: 步骤 3 改为自动循环

**选择**: 步骤 3 替换为：执行完当前轮 ready stages 后，自动回到步骤 1 查询状态，如果有新的 ready stages 则继续执行，直到 completed 或 failed。

**理由**: 这是最简单的循环结构，复用步骤 1-2 的现有逻辑，无需额外抽象。

### 决策 3: SKILL_FILES 列表需要更新

**选择**: 在 `init_cmd.py` 的 `SKILL_FILES` 常量中添加 `"ll-ff.md"`。

**理由**: `init` 命令通过遍历 `SKILL_FILES` 列表将模板复制到 `.claude/commands/`，新模板必须加入此列表才能被自动注入。

## Risks / Trade-offs

- **[风险] 长流水线可能占用大量 Agent context** → 缓解：这是 Agent 的固有限制，用户可以选择用 `/ll-run` 分轮执行来控制单次 context 使用量
- **[风险] 中间 stage 失败时所有后续工作丢失** → 缓解：ll-chain 的状态管理确保已完成的 stage 状态已持久化，用户可以修复后从失败点继续