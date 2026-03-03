## Why

`flows` 命令仅从项目级 `.llchain/schemas/` 加载 schema，用户无法复用个人定义的全局 schema 模板。同时 `build_stage_context` 仅在入口节点（无依赖）时才注入用户 instruction，导致下游节点无法获取用户意图上下文，降低了 Agent 执行质量。

## What Changes

- `flows` 命令新增对用户级 schema 目录 `~/.local/share/llchain/schemas` 的扫描，项目级同名 schema 优先
- `build_stage_context` 修改 instruction 组装逻辑：所有 stage 均包含用户 instruction（而非仅入口节点）
- `status` 命令输出中，仅在 ready stage 无依赖时展示用户 instruction 信息

## Capabilities

### New Capabilities
- `user-schema-loading`: flows 命令支持从用户级目录加载 schema 并与项目级合并，项目级优先

### Modified Capabilities
- `stage-instruction`: 修改 instruction 分发策略，所有 stage 均携带用户 instruction

## Impact

- 涉及文件：`commands/flows.py`、`core/context.py`、`commands/status.py`
- 新增常量：用户级 schema 目录路径（`constants.py`）
- 需更新对应单元测试