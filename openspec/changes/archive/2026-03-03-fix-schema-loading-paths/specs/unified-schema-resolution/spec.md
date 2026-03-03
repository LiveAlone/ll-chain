## ADDED Requirements

### Requirement: 单个 schema 按优先级查找

系统 SHALL 提供 `resolve_schema_path(flow_id)` 函数，按以下顺序查找 schema 文件：
1. 项目目录：`.llchain/schemas/{flow_id}.yaml`
2. 用户目录：`~/.local/share/llchain/schemas/{flow_id}.yaml`

项目目录优先。找到第一个即返回其路径。

#### Scenario: 仅项目目录存在
- **WHEN** schema 文件仅存在于项目目录
- **THEN** 返回项目目录下的路径

#### Scenario: 仅用户目录存在
- **WHEN** schema 文件仅存在于用户目录
- **THEN** 返回用户目录下的路径

#### Scenario: 两个目录都存在
- **WHEN** 同 id 的 schema 在两个目录都存在
- **THEN** 返回项目目录下的路径（项目优先）

#### Scenario: 都不存在
- **WHEN** schema 文件在两个目录都不存在
- **THEN** 抛出错误提示 schema 不存在

### Requirement: 批量加载所有 schema

系统 SHALL 提供 `load_all_schemas()` 函数，从用户目录和项目目录加载所有 schema，项目目录的同 id schema 覆盖用户目录的。

#### Scenario: 合并两个目录的 schema
- **WHEN** 用户目录有 schema A、B，项目目录有 schema B、C
- **THEN** 返回 A（来自用户目录）、B（来自项目目录，覆盖）、C（来自项目目录）

#### Scenario: 用户目录不存在
- **WHEN** 用户 schema 目录不存在
- **THEN** 仅返回项目目录的 schema，不报错

### Requirement: 所有命令使用统一入口

`create`、`status`、`stage` 命令 SHALL 使用 `resolve_schema_path` 查找 schema。`flows` 命令 SHALL 使用 `load_all_schemas` 加载 schema 列表。

#### Scenario: create 使用用户级 schema
- **WHEN** 用户执行 `ll-chain create my-task --flow user-schema`，且该 schema 仅存在于用户目录
- **THEN** 成功创建 task

#### Scenario: status 使用用户级 schema
- **WHEN** task 关联的 flow schema 仅存在于用户目录
- **THEN** `status` 命令正常返回状态

#### Scenario: stage 使用用户级 schema
- **WHEN** task 关联的 flow schema 仅存在于用户目录
- **THEN** `stage` 命令正常返回 context