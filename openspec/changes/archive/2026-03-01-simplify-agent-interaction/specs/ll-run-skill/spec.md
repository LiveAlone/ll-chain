## ADDED Requirements

### Requirement: /ll-run 查询 task 状态并判断终止条件

`/ll-run` 执行时 SHALL 首先调用 `ll-chain status $ARGUMENTS` 获取 task 当前状态，并根据以下条件判断是否终止：

- `status: completed` → 提示用户 task 已全部完成，结束
- `status: failed` → 提示用户存在 failed stages，结束
- `ready_stages` 为空 → 提示用户无可执行 stage，结束

#### Scenario: task 已完成

- **WHEN** 用户执行 `/ll-run A`，且 `ll-chain status A` 返回 `status: completed`
- **THEN** `/ll-run` 提示用户 "Task A 已全部完成"，不执行任何 stage

#### Scenario: task 有失败的 stage

- **WHEN** 用户执行 `/ll-run A`，且 `ll-chain status A` 返回 `status: failed`
- **THEN** `/ll-run` 提示用户存在 failed stages，不执行任何 stage

#### Scenario: 无 ready stages

- **WHEN** 用户执行 `/ll-run A`，且 `ll-chain status A` 返回 `ready_stages` 为空列表
- **THEN** `/ll-run` 提示用户当前无可执行 stage

### Requirement: /ll-run 顺序执行当前轮所有 ready stages

当 `ready_stages` 非空时，`/ll-run` SHALL 按列表顺序逐个执行每个 ready stage。对每个 stage 按以下流程执行：

1. 调用 `ll-chain update {task} {node} running` 将状态设为 running
2. 调用 `ll-chain stage {task} {node}` 获取任务详情
3. 加载两层 Context（constraints + dependency summaries）
4. 综合 `instruction.prompts` 中所有指令和上下文执行任务
5. 将输出保存到 `output_dir`（MUST 包含 `summary.md`）
6. 调用 `ll-chain update {task} {node} completed` 将状态设为 completed

#### Scenario: 单个 ready stage 成功执行

- **WHEN** `ready_stages` 为 `[analyze]`
- **THEN** `/ll-run` 执行 analyze stage 的完整 6 步流程，analyze 状态从 pending 变为 completed

#### Scenario: 多个 ready stages 顺序执行

- **WHEN** `ready_stages` 为 `[analyze, security]`
- **THEN** `/ll-run` 先完整执行 analyze 的 6 步流程，再完整执行 security 的 6 步流程，两者均变为 completed

### Requirement: /ll-run 加载两层 Context

执行 stage 时，`/ll-run` SHALL 加载两层上下文：

- **Layer 1**: 读取 `constraints` 列表，作为执行过程的硬约束
- **Layer 2**: 对 `dependencies` 中每个依赖节点，读取其 `summary` 路径指向的 `summary.md` 文件；如需更多细节可进入 `output_dir` 读取其他文件

#### Scenario: 入口节点无依赖

- **WHEN** 执行入口节点（`dependencies` 为空列表）
- **THEN** `/ll-run` 仅加载 Layer 1 constraints，综合 `instruction.prompts`（可能包含 schema prompt 和 user instruction）执行任务

#### Scenario: 非入口节点有上游依赖

- **WHEN** 执行非入口节点，`dependencies` 包含 `[{node: analyze, summary: .llchain/A/stage-analyze/summary.md}]`
- **THEN** `/ll-run` 加载 Layer 1 constraints，并读取 `stage-analyze/summary.md` 的内容作为 Layer 2 上下文

### Requirement: /ll-run 每个 stage 必须输出 summary.md

每个 stage 执行完成后，MUST 在 `output_dir` 目录下生成 `summary.md` 文件。可额外输出 `.md`、`.json` 等其他文件。

#### Scenario: 正常输出

- **WHEN** stage 执行完毕
- **THEN** `output_dir` 目录下存在 `summary.md` 文件，内容为任务执行的关键产出摘要

### Requirement: /ll-run 失败即停

当前轮中某个 stage 执行失败时，`/ll-run` SHALL 立即停止，不继续执行同轮的其他 ready stages。

1. 调用 `ll-chain update {task} {node} failed` 将失败 stage 状态设为 failed
2. 告知用户哪个 stage 失败及原因
3. 不继续执行剩余 ready stages

#### Scenario: 第一个 stage 失败

- **WHEN** `ready_stages` 为 `[analyze, security]`，且 analyze 执行失败
- **THEN** `/ll-run` 将 analyze 状态设为 failed，告知用户 analyze 失败，不执行 security

#### Scenario: 第二个 stage 失败

- **WHEN** `ready_stages` 为 `[analyze, security]`，analyze 执行成功，security 执行失败
- **THEN** analyze 状态为 completed，security 状态为 failed，`/ll-run` 告知用户 security 失败

### Requirement: /ll-run 执行完毕后引导用户下一步

当前轮所有 ready stages 执行完毕后，`/ll-run` SHALL 再次调用 `ll-chain status` 查看后续状态，并输出引导信息：

- 全部 stage completed → 提示 "Task 已全部完成！查看 .llchain/{task}/"
- 还有后续 ready stages → 提示 "执行 /ll-run {task} 继续下一阶段"

#### Scenario: 还有后续 stages

- **WHEN** 当前轮 `[analyze, security]` 执行完毕，再次查状态发现 `ready_stages: [report]`
- **THEN** `/ll-run` 提示用户 "analyze, security 已完成！执行 /ll-run A 继续下一阶段"

#### Scenario: 全部完成

- **WHEN** 当前轮 `[report]` 执行完毕，再次查状态发现 `status: completed`
- **THEN** `/ll-run` 提示用户 "Task A 已全部完成！查看 .llchain/A/ 获取结果"

### Requirement: 删除 /ll-worker Skill

`/ll-worker` Skill SHALL 被完全移除：

- 删除 `src/ll_chain/templates/ll-worker.md` 模板文件
- 从 `init_cmd.py` 的 `SKILL_FILES` 列表中移除 `"ll-worker.md"` 条目
- `ll-chain init` 不再将 `ll-worker.md` 注入到 `.claude/commands/`

#### Scenario: 新项目初始化

- **WHEN** 用户在新项目执行 `ll-chain init`
- **THEN** `.claude/commands/` 目录下仅包含 `ll-run.md` 和 `ll-create.md`，不包含 `ll-worker.md`

### Requirement: 更新项目文档

CLAUDE.md 中关于架构的描述 SHALL 同步更新：

- "三层分工"改为"两层分工"
- 移除 Worker 相关描述
- 更新 `/ll-run` 的职责描述

#### Scenario: CLAUDE.md 内容一致性

- **WHEN** 变更完成后查看 CLAUDE.md
- **THEN** 文档中不再包含 "三层分工"、"Worker"、"/ll-worker" 等旧术语，架构描述与 `docs/design.md` 保持一致
