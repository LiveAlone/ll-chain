## Context

当前 `flows` 命令仅从 `LLCHAIN_DIR / "schemas"` 加载 schema 文件，用户无法定义全局可复用的 schema 模板。`build_stage_context` 中 user instruction 仅注入到入口节点（`depends_on` 为空），导致有依赖的下游节点缺乏用户意图上下文。

## Goals / Non-Goals

**Goals:**
- `flows` 命令同时扫描用户级目录 `~/.local/share/llchain/schemas` 和项目级目录，同名时项目级优先
- 所有 stage 的 instruction prompts 中都包含 user instruction（如果存在）
- `status` 命令在输出中展示 user instruction（仅当 ready stage 无依赖时）

**Non-Goals:**
- 不涉及 schema 合并或继承机制（同名直接覆盖）
- 不修改 `create` 命令的 schema 查找逻辑（本次仅影响 `flows` 列表展示）
- 不变更 instruction 的存储结构

## Decisions

### 1. 用户级 schema 目录路径

使用 `~/.local/share/llchain/schemas`，遵循 XDG Base Directory 规范中的 `XDG_DATA_HOME` 惯例。在 `constants.py` 中新增 `USER_SCHEMAS_DIR` 常量，基于 `Path.home()` 计算。

**备选方案**：使用 `~/.llchain/schemas` — 简单但不符合 XDG 规范，已排除。

### 2. 项目级优先的合并策略

先加载用户级 schema，再加载项目级 schema，以 `schema.id` 为 key 用 dict 去重。后加载的项目级会覆盖同 id 的用户级 schema。

### 3. instruction 分发策略变更

移除 `build_stage_context` 中 `if not node.depends_on` 的限制条件，使所有 stage 均可获得 user instruction。保持 prompts 列表结构不变：schema prompt 在前，user instruction 在后。

### 4. status 命令中 instruction 展示

在 `status` 命令的输出 dict 中新增 `instruction` 字段。仅当 task 有 instruction 时才输出该字段。

## Risks / Trade-offs

- **用户目录不存在时的处理** → 若 `~/.local/share/llchain/schemas` 不存在，静默跳过，不报错
- **下游节点 instruction 冗余** → 所有 stage 都带 user instruction 会略增输出体积，但相比 Agent 决策质量提升可忽略