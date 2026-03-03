## ADDED Requirements

### Requirement: 自动推断 task 名称
当用户执行 `/ll-run` 且未提供 `$ARGUMENTS` 时，skill 须通过 `ll-chain list --json` 查询现有 task 列表，并根据数量自动处理。

#### Scenario: 仅有一个 task
- **WHEN** 用户执行 `/ll-run`（无参数），且 `ll-chain list --json` 返回恰好 1 个 task
- **THEN** 自动将该 task 作为当前执行目标，无需用户确认，继续后续步骤

#### Scenario: 没有 task
- **WHEN** 用户执行 `/ll-run`（无参数），且 `ll-chain list --json` 返回空列表
- **THEN** 提示用户当前无可用 task，并引导用户通过 `/ll-create` 或 `ll-chain create` 创建

#### Scenario: 多个 task
- **WHEN** 用户执行 `/ll-run`（无参数），且 `ll-chain list --json` 返回 2 个或以上 task
- **THEN** 列出所有 task 的名称和状态，让用户选择要执行的 task

#### Scenario: 用户显式传入 task 名称
- **WHEN** 用户执行 `/ll-run <task_name>` 提供了具体参数
- **THEN** 直接使用该参数作为 task 名称，跳过推断逻辑
