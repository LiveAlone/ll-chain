## ADDED Requirements

### Requirement: ll-ff 模板文件存在
系统 SHALL 在 `src/ll_chain/templates/` 目录下提供 `ll-ff.md` 模板文件。

#### Scenario: 模板文件存在
- **WHEN** 查看 `src/ll_chain/templates/` 目录
- **THEN** 目录中包含 `ll-ff.md` 文件

### Requirement: ll-ff 模板步骤 0-2 与 ll-run 一致
`ll-ff.md` 的步骤 0（确定 task）、步骤 1（查询状态）、步骤 2（顺序执行所有 ready stages）SHALL 与 `ll-run.md` 保持完全一致。

#### Scenario: 步骤 0 确定 task
- **WHEN** 用户调用 `/ll-ff` 并提供 `$ARGUMENTS`
- **THEN** 行为与 `/ll-run` 的步骤 0 完全相同（支持自动选择、列表选择等）

#### Scenario: 步骤 1 查询状态
- **WHEN** 执行步骤 1 查询 task 状态
- **THEN** 终止条件判断逻辑与 `/ll-run` 完全相同

#### Scenario: 步骤 2 执行 ready stages
- **WHEN** 执行步骤 2 顺序执行 ready stages
- **THEN** 2a/2b/2c/2d 四个子步骤与 `/ll-run` 完全相同

### Requirement: ll-ff 步骤 3 自动循环执行
步骤 3 SHALL 在当前轮 ready stages 全部执行成功后，自动回到步骤 1 查询状态并继续执行下一轮，直到 task 完成或失败。

#### Scenario: 当前轮成功且有后续 stages
- **WHEN** 当前轮所有 ready stages 执行成功
- **AND** 再次查询状态发现有新的 ready stages
- **THEN** 自动回到步骤 1 继续执行下一轮

#### Scenario: 当前轮成功且 task 已完成
- **WHEN** 当前轮所有 ready stages 执行成功
- **AND** 再次查询状态显示 `status: completed`
- **THEN** 提示 "Task {task_name} 已全部完成！查看 .llchain/{task_name}/ 获取结果"，结束

#### Scenario: 当前轮执行失败
- **WHEN** 当前轮某个 stage 执行失败
- **THEN** 立即终止，不继续执行后续 stage 或后续轮次

### Requirement: ll-ff 硬约束与 ll-run 一致
`ll-ff.md` SHALL 包含与 `ll-run.md` 相同的硬约束部分，确保 summary.md 生成要求、失败停止和代码文件保护规则不变。

#### Scenario: 硬约束内容一致
- **WHEN** 比较 `ll-ff.md` 和 `ll-run.md` 的硬约束部分
- **THEN** 除步骤 3 相关描述外，所有硬约束规则完全相同

### Requirement: init 命令注入 ll-ff 模板
`init_cmd.py` 中的 `SKILL_FILES` 常量 SHALL 包含 `"ll-ff.md"`，确保 `ll-chain init` 命令将该模板复制到 `.claude/commands/` 目录。

#### Scenario: init 命令复制 ll-ff.md
- **WHEN** 执行 `ll-chain init`
- **THEN** `.claude/commands/ll-ff.md` 文件被创建（如不存在）
