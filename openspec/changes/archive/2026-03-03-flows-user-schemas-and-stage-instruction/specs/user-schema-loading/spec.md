## ADDED Requirements

### Requirement: flows 命令加载用户级 schema
`flows` 命令除扫描项目级 `LLCHAIN_DIR / "schemas"` 外，还须扫描用户级目录 `~/.local/share/llchain/schemas` 下的 `.yaml` 文件。

#### Scenario: 用户级目录存在且包含 schema
- **WHEN** 用户级目录 `~/.local/share/llchain/schemas` 存在且包含有效的 schema YAML 文件
- **THEN** `flows` 命令的输出须包含该用户级 schema

#### Scenario: 用户级目录不存在
- **WHEN** 用户级目录 `~/.local/share/llchain/schemas` 不存在
- **THEN** `flows` 命令正常运行，仅输出项目级 schema，不报错

#### Scenario: 同名 schema 项目级优先
- **WHEN** 项目级和用户级目录中存在相同 `id` 的 schema
- **THEN** `flows` 命令输出中使用项目级 schema 的内容，用户级同 id schema 被覆盖

### Requirement: 新增用户级 schema 目录常量
系统须在 `constants.py` 中定义 `USER_SCHEMAS_DIR` 常量，值为 `Path.home() / ".local" / "share" / "llchain" / "schemas"`。

#### Scenario: 常量可被正确引用
- **WHEN** 代码中引用 `USER_SCHEMAS_DIR`
- **THEN** 其值为用户 home 目录下 `.local/share/llchain/schemas` 的绝对路径
