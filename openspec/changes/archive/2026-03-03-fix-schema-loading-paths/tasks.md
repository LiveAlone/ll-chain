## 1. 提取统一 schema 查找模块

- [x] 1.1 新建 `src/ll_chain/core/schema_resolver.py`，实现 `resolve_schema_path(flow_id: str) -> Path` 函数（项目目录优先 → 用户目录回退 → 不存在抛异常）
- [x] 1.2 在同文件实现 `load_all_schemas() -> dict[str, Schema]` 函数（先加载用户目录，再加载项目目录覆盖同 id）

## 2. 修改命令使用统一入口

- [x] 2.1 修改 `commands/create.py`：用 `resolve_schema_path(flow)` 替代硬编码路径
- [x] 2.2 修改 `commands/status.py`：用 `resolve_schema_path(task.flow)` 替代硬编码路径
- [x] 2.3 修改 `commands/stage.py`：用 `resolve_schema_path(task.flow)` 替代硬编码路径
- [x] 2.4 修改 `commands/flows.py`：用 `load_all_schemas()` 替代内联的双目录遍历逻辑

## 3. 测试

- [x] 3.1 新建 `tests/core/test_schema_resolver.py`，覆盖 spec 中所有场景（仅项目目录、仅用户目录、双目录覆盖、都不存在、用户目录不存在）