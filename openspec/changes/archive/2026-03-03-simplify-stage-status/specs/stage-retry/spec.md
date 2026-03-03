## ADDED Requirements

### Requirement: Stage 状态重置为 pending

系统 SHALL 允许通过 `update` 命令将 `failed` 状态的 stage 重置为 `pending`，以支持重试执行。

#### Scenario: 将 failed stage 重置为 pending

- **WHEN** 用户执行 `ll-chain update <task> <node> pending` 且该 stage 当前状态为 `failed`
- **THEN** stage 状态变更为 `pending`，`completed_at` 字段被清除，task 状态根据所有 stages 重新推导

#### Scenario: 重置后 stage 出现在 ready_stages 中

- **WHEN** 一个 `failed` stage 被重置为 `pending`，且其所有依赖节点均为 `completed`
- **THEN** 该 stage 出现在 `compute_ready_stages` 返回的列表中，可被 Agent 再次执行

### Requirement: 三态状态模型

stage 状态 SHALL 仅包含 `pending`、`completed`、`failed` 三种有效值。系统 MUST 拒绝任何其他状态值。

#### Scenario: 拒绝无效状态值

- **WHEN** 用户执行 `ll-chain update <task> <node> running`
- **THEN** 系统返回错误，提示 `running` 不是有效状态值，有效值为 `(pending, completed, failed)`

#### Scenario: update 命令接受 pending 作为有效状态

- **WHEN** 用户执行 `ll-chain update <task> <node> pending`
- **THEN** 系统接受该操作，将 stage 状态设为 `pending`

### Requirement: Task 状态推导不包含 running

`derive_task_status` SHALL 仅返回 `pending`、`completed`、`failed` 三种值。不再存在 task 级别的 `running` 状态。

#### Scenario: 所有 stage 为 pending 时 task 状态为 pending

- **WHEN** task 中所有 stage 的状态均为 `pending`
- **THEN** `derive_task_status` 返回 `pending`

#### Scenario: 混合 pending 和 completed 时 task 状态为 pending

- **WHEN** task 中部分 stage 为 `completed`、部分为 `pending`
- **THEN** `derive_task_status` 返回 `pending`

#### Scenario: 任一 stage 为 failed 时 task 状态为 failed

- **WHEN** task 中至少一个 stage 状态为 `failed`
- **THEN** `derive_task_status` 返回 `failed`

### Requirement: StageState 不包含 started_at 字段

`StageState` 数据模型 SHALL 仅包含 `status` 和 `completed_at` 字段，不再包含 `started_at`。

#### Scenario: StageState 序列化不输出 started_at

- **WHEN** 对一个 `StageState` 实例调用 `to_dict()`
- **THEN** 返回的字典中不包含 `started_at` 键

### Requirement: status 命令输出不包含 running_stages

`status` 命令的返回结构 SHALL 不包含 `running_stages` 字段。

#### Scenario: status 命令返回结构

- **WHEN** 用户执行 `ll-chain status <task>`
- **THEN** 返回中包含 `ready_stages`、`completed_stages`、`failed_stages`，不包含 `running_stages`