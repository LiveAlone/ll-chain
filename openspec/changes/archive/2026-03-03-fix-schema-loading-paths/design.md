## Context

当前 `flows` 命令正确地从两个目录加载 schema（先用户目录 `~/.local/share/llchain/schemas/`，再项目目录 `.llchain/schemas/`，项目级覆盖同 id）。但 `create`、`status`、`stage` 三个命令只从项目目录查找 schema 文件，导致用户级 schema 在这些命令中不可用。

受影响的代码点（均硬编码 `LLCHAIN_DIR / "schemas" / f"{flow}.yaml"`）：
- `commands/create.py:20`
- `commands/status.py:23`
- `commands/stage.py:25`
- `commands/flows.py:16-28` — 逻辑正确但为内联实现，需统一

## Goals / Non-Goals

**Goals:**
- 提取统一的 schema 查找函数，所有命令通过同一入口加载 schema
- 项目目录优先级高于用户目录（保持 `flows` 命令现有语义）
- `flows` 命令也走统一入口，保证代码一致性

**Non-Goals:**
- 不改变 Schema 数据模型
- 不增加新的 schema 目录来源
- 不修改 `init` 命令的 schema 注入逻辑

## Decisions

### 1. 新建 `core/schema_resolver.py`，提取两个函数

- `resolve_schema_path(flow_id: str) -> Path`：按项目目录 → 用户目录顺序查找单个 schema 文件，不存在则抛 `click.ClickException`
- `load_all_schemas() -> dict[str, Schema]`：加载所有 schema（先用户目录低优先级，再项目目录高优先级覆盖），供 `flows` 命令使用

**备选方案**：
- 放在 `utils/` 下 — 不合适，这是核心业务逻辑
- 内联到各命令 — 违反 DRY 原则

### 2. 四个命令统一改为调用新函数

- `create`、`status`、`stage`：`resolve_schema_path(flow_id)` 替代硬编码路径
- `flows`：`load_all_schemas()` 替代内联的双目录遍历逻辑

## Risks / Trade-offs

- **[风险] 改动多个命令** → 逻辑简单，单元测试覆盖即可
- **[取舍] 新增文件** → 增加 `core/schema_resolver.py`，但保持职责单一，优于分散在各命令中