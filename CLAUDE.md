# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ll-chain 是一个 AI 工作流编排 CLI 工具，为 Claude Code 等 AI Agent 提供流水线定义、状态管理和执行协调能力。核心设计理念：**CLI 不思考，只读写文件；所有决策在 Agent 侧。**

- **Python**: >=3.11
- **包管理**: uv（`uv_build` backend）
- **CLI 框架**: click
- **数据格式**: YAML（schema, task, config）
- **入口**: `ll_chain:main` → 注册为 `ll-chain` CLI script

## Common Commands

```bash
uv sync                          # 安装依赖
uv run ll-chain                  # 运行 CLI
uv run pytest                    # 运行全部测试
uv run pytest tests/core/test_dag.py::TestValidateDag::test_valid_dag  # 单个测试
make install                     # 全局安装（uv tool install --editable）
make uninstall                   # 全局卸载
```

## Architecture

### 两层分工

1. **ll-chain CLI**（薄工具）— 无状态纯文件操作：依赖解析、读写 task/schema、拼装 stage context
2. **Agent**（/ll-run skill）— 流程编排 + 实际执行：查 status、加载两层上下文、顺序执行当前轮 ready stages、输出结果、引导用户执行下一轮

### 核心概念

- **Schema**: 流水线模板（`schemas/` 目录下的 YAML），定义 DAG 结构
- **Flow**: 用户定义的有向无环图，通过 `depends_on` 声明节点间依赖
- **Task**: 基于 Schema 创建的执行实例，存储在 `.llchain/<task_name>/task.yaml`
- **Stage**: Task 执行某个 Node 时的运行单元，状态流转：`pending → running → completed/failed`

### 代码结构

- `cli.py` — click group，注册所有子命令
- `commands/` — 每个子命令一个文件（init, create, list, status, stage, update, flows）
- `models/` — dataclass 数据类：Schema/Node/NodeContext, Task/StageState, Config
- `core/dag.py` — DAG 逻辑：validate_dag, compute_ready_stages, derive_task_status
- `core/context.py` — build_stage_context，组装两层 Context 给 Agent
- `templates/` — Skill 模板文件（ll-create.md, ll-run.md），`init` 命令会复制到 `.claude/commands/`
- `utils/` — yaml_io（load/save/dump）、output（YAML/JSON 双格式输出）

### 关键模式

- **所有命令支持 `--json` flag**，默认输出 YAML，加 `--json` 输出 JSON
- **命令统一结构**：检查 `LLCHAIN_DIR` 存在 → 加载 models → 执行逻辑 → `output_result(data, as_json)`
- **Models 使用 dataclass**，不用 pydantic，手动实现 `load()`/`save()`/`to_dict()`
- **DAG 逻辑集中在 `core/dag.py`**：拓扑排序检测环、计算 ready stages、推导 task 状态
- **两层 Context 模型**（`core/context.py`）：Layer 1 = 全局 constraints，Layer 2 = 上游节点的 summary.md 路径。`instruction` 字段为 `prompts` 列表结构（`[{source, content}]`），入口节点可包含 user instruction。用户通过 `/ll-run` 手动驱动每一轮 DAG 执行
- **错误处理**：统一使用 `click.ClickException`，错误信息用中文
- **Skill 注入**：`init` 命令将 `templates/` 下的 `.md` 文件复制到 `.claude/commands/`，已存在则跳过

### 文件布局（运行时）

```
.llchain/
├── config.yaml         # 全局配置（constraints, default_flow_id）
├── schemas/            # Flow 定义模板
└── <task_name>/        # Task 实例
    ├── task.yaml       # 状态文件（含可选 instruction）
    └── stage-<node>/   # Stage 输出（必含 summary.md）
```

### 测试结构

测试目录镜像源码结构：`tests/core/`, `tests/commands/`, `tests/models/`。测试用 pytest，直接构造 dataclass 实例（如 `Node`, `StageState`）进行单元测试，不依赖文件系统 fixture。

详细设计见 `docs/design.md`。