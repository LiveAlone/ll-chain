## Context

当前 ll-chain 的 stage 状态模型包含 4 种状态：`pending | running | failed | completed`。Agent 执行 stage 时需要两步更新：先 `update running`，执行完后 `update completed/failed`。这带来两个问题：

1. **中断卡死**：如果 Agent 在 `running` 阶段被中断，stage 停留在 `running`，不会出现在 `ready_stages` 中，task 卡死
2. **流程冗余**：`running` 状态对 CLI 工具层面无实际意义（CLI 不追踪进程），仅增加了一次额外的命令调用

## Goals / Non-Goals

**Goals:**
- 将 stage 状态简化为 `pending | completed | failed` 三态
- 天然支持中断后重复执行（`pending` 的 stage 始终可被再次拾起）
- 支持 `failed` stage 重置为 `pending` 以便重试
- 简化 `ll-run` 执行协议，减少一次 `update` 命令调用
- 同步更新 `docs/design.md` 架构文档，保持文档与实现一致

**Non-Goals:**
- 不引入执行历史或审计日志
- 不实现自动重试机制（重试由用户手动触发）
- 不修改 DAG 拓扑结构或依赖解析逻辑

## Decisions

### 决策 1：移除 `running` 状态而非添加恢复机制

**选择**：直接移除 `running` 状态

**备选方案**：保留 `running` 但增加超时恢复机制（如 `running` 超过 N 分钟自动回退 `pending`）

**理由**：ll-chain 是纯文件操作的薄工具，无守护进程来检测超时。`running` 状态在当前架构下无实际用途——CLI 不监控进程状态，Agent 侧可以通过文件系统自行判断执行中状态。直接移除最简单、最彻底。

### 决策 2：移除 `started_at` 字段

**选择**：随 `running` 状态一起移除 `StageState.started_at`

**备选方案**：保留 `started_at`，在 stage 从 `pending` 变为 `completed/failed` 时记录

**理由**：`started_at` 原本记录进入 `running` 的时刻。移除 `running` 后，没有明确的"开始"语义。`completed_at` 已经记录了完成时间，足以满足基本时间追踪需求。保持模型精简。

### 决策 3：支持 `failed → pending` 状态回退

**选择**：`update` 命令允许将 `failed` 的 stage 设为 `pending`

**理由**：当前模型下 `failed` 是终态，用户没有简单的方式重试单个 stage。允许回退到 `pending` 配合去掉 `running` 后的幂等执行，提供了自然的重试路径。不需要额外的 `retry` 命令，只需放宽 `update` 的状态转移规则。

### 决策 4：`derive_task_status` 不再返回 `running`

**选择**：task 级别状态也简化为 `pending | completed | failed`

**理由**：task 状态由 stages 推导而来。移除 stage 的 `running` 后，task 也不会再有 `running` 状态。逻辑简化为：任一 stage 为 `failed` → task `failed`；全部 `completed` → task `completed`；其余 → `pending`。

### 决策 5：同步更新架构文档

**选择**：在同一变更中更新 `docs/design.md`

**理由**：`docs/design.md` 是项目核心架构文档，多处引用了 `running` 状态（§5.3 状态流转图、§6.4 task.yaml 示例、§9 执行协议、§10 交互流程）。代码变更后如果文档不同步，会误导后续开发。

## Risks / Trade-offs

**[无法区分"从未执行"和"执行中"的 stage]** → 这是有意为之的简化。Agent 侧如果需要追踪执行进度，可以通过检查 `output_dir` 是否存在来判断。CLI 层面不需要这个区分。

**[现有 task.yaml 兼容性]** → 已有的 `running` 状态 task.yaml 将无法正常工作。由于项目处于早期阶段，直接破坏性变更即可，无需迁移脚本。

**[`failed → pending` 可能导致循环]** → 用户可以反复重试 failed stage。这是期望行为，不是问题。如果 stage 持续失败，用户自行判断是否继续重试。