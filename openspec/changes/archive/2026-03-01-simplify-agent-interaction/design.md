## Context

ll-chain 当前采用三层架构：CLI（薄工具）→ MainAgent（/ll-run，纯编排）→ Worker（/ll-worker，SubAgent 执行）。MainAgent 通过 `Task(SubAgent)` 派发 Worker 处理每个 stage，整条流水线在一次 `/ll-run` 调用中自动跑完。

这带来两个问题：
1. SubAgent 交互增加了复杂度（MainAgent 需要管理 SubAgent 生命周期和状态同步）
2. 用户对中间过程无感知，无法在 DAG 层级之间审查结果

本次变更将三层简化为两层：CLI + Agent（/ll-run），用户手动驱动每一轮 DAG 执行。

## Goals / Non-Goals

**Goals:**

- 去除 SubAgent（/ll-worker）交互，将 Worker 的 stage 执行逻辑融合到 /ll-run 中
- 改为 human-in-the-loop 模型：每次 `/ll-run` 执行当前轮所有 ready stages，完成后引导用户手动触发下一轮
- 保持 CLI 命令层完全不变（status, stage, update 等）
- 保持两层 Context 加载逻辑不变（constraints + dependency summaries）

**Non-Goals:**

- 不修改 CLI 命令的接口或行为
- 不修改 `/ll-create` Skill
- 不修改 Schema/Task/Config 数据模型
- 不引入新的 CLI 命令

## Decisions

### D1: /ll-run 每次执行当前轮所有 ready stages

**选择**: 一次 `/ll-run` 调用顺序执行所有 ready stages，而非一次只执行一个。

**理由**: 同一轮 ready stages 之间没有依赖关系（它们是 DAG 中同一层的并行节点），不需要用户逐个审查。review 的价值在 DAG 层级之间——上游节点完成后、下游节点开始前。

**替代方案**: 一次只执行一个 stage，用户连续调多次。被否决——增加了用户操作次数，没有额外收益。

### D2: 失败即停，不继续后续同轮 stage

**选择**: 当前轮中某个 stage 执行失败后，立即停止，不继续执行同轮的其他 ready stages。

**理由**: 与现有的"失败即停"策略保持一致。用户需要介入处理失败，继续执行其他 stage 可能浪费资源。

### D3: 执行完毕后再查一次 status 以确定引导信息

**选择**: 当前轮所有 stages 执行完毕后，再调用一次 `ll-chain status` 来判断下一步引导内容。

**理由**: 能准确区分"还有后续 stages → 引导 /ll-run"和"全部完成 → 告知完成"两种情况，避免硬编码判断逻辑。

### D4: 删除 ll-worker.md 模板文件而非留空

**选择**: 直接删除 `src/ll_chain/templates/ll-worker.md` 文件，同时从 `SKILL_FILES` 列表中移除。

**理由**: 保留空文件会造成困惑。`init` 命令的 `_inject_skills()` 遍历 `SKILL_FILES` 列表注入 Skill，移除列表项即可停止注入。

### D5: Stage 执行协议从 5 步简化为 4 步

**选择**: 移除原 Worker 协议中的第 5 步（RETURN — 返回 completed/failed），保留 QUERY → LOAD CONTEXT → EXECUTE → OUTPUT。

**理由**: 原 RETURN 步骤是 SubAgent 向 MainAgent 返回执行结果的通信机制。合并后，/ll-run 自身执行 stage，状态更新（`ll-chain update`）直接在流程中完成，不需要额外的返回步骤。

## Risks / Trade-offs

**[单轮执行时间变长]** → 同轮多个 stage 顺序执行可能耗时较长（原方案中 SubAgent 也是顺序的，所以实际无变化）

**[用户需多次手动触发]** → 相比原方案一次跑完，用户需要按 DAG 层数手动执行 `/ll-run` 多次 → 这是有意为之的 trade-off，换取了中间结果可审查

**[已部署用户需重新 init]** → 已有 `.claude/commands/ll-worker.md` 的项目不会被自动清理 → 用户手动删除即可，影响范围小（个人工具）