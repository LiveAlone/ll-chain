## Why

`flows` 命令加载 schema 时同时搜索用户目录（`~/.local/share/llchain/schemas/`）和项目目录（`.llchain/schemas/`），但 `create`、`status`、`stage` 等命令只从项目目录加载。这导致用户级 schema 在 `flows` 中可见，但无法用于创建和执行 task。

## What Changes

- 提取统一的 schema 查找函数，按优先级搜索项目目录和用户目录
- 修改 `create`、`status`、`stage`、`flows` 所有命令使用统一查找函数
- `flows` 命令现有逻辑正确，作为参考实现提取为统一入口，保证代码一致性

## Capabilities

### New Capabilities

- `unified-schema-resolution`: 统一 schema 文件查找逻辑，所有命令使用一致的多目录搜索策略

### Modified Capabilities

## Impact

- 受影响文件：`commands/create.py`、`commands/status.py`、`commands/stage.py`、`commands/flows.py`
- 新增工具函数位置：`core/` 或 `utils/` 下
- 不影响 Schema 数据结构，不影响 task.yaml 格式
- 向后兼容：项目目录优先级仍高于用户目录