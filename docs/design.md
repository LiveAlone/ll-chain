# ll-chain 设计文档

> AI 工作流编排工具 —— 为 Claude Code / OpenCode 设计的轻量级流水线管理器

## 1. 项目定位

ll-chain 是一个命令行工具，作为 AI Agent（如 Claude Code）的外挂，提供 **流水线定义、状态管理和执行协调** 能力。

核心价值：
- **持久化状态** —— Agent 的 context window 会丢失，`.llchain/` 里的状态文件不会
- **可复用流程** —— 定义一次，多次执行，跨项目复用
- **跨会话恢复** —— Agent 崩溃或超时后，新会话可以从断点继续
- **协议标准化** —— 统一 Agent 与流水线交互的方式，不绑定特定 AI 工具

## 2. 核心概念

| 概念 | 说明 |
|------|------|
| **Schema** | 流水线模板文件，存放于 `schemas/` 目录 |
| **Flow** | 用户定义的 DAG（有向无环图），描述流程逻辑 |
| **Node** | Flow 中的节点，定义单个任务的 prompt、依赖、上下文 |
| **Task** | 基于 Flow 创建的执行实例，同一 Flow 可创建多个 Task |
| **Stage** | Task 执行某个 Node 时的运行单元，包含状态和输出 |

## 3. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      ll-chain 全貌                           │
│                                                             │
│  .llchain/                                                  │
│  ├── config.yaml           ← 全局配置（constraints 等）      │
│  ├── schemas/              ← Flow 定义模板 (DAG)            │
│  ├── A/                    ← Task 实例                      │
│  │     ├── task.yaml       ← 状态文件 (CLI 维护)            │
│  │     ├── stage-analyze/  ← Stage 输出                     │
│  │     └── stage-report/                                    │
│  └── B/                    ← 另一个 Task 实例               │
│                                                             │
│  CLI 命令 (薄工具):                                          │
│    init / create / list / status / stage / update / flows   │
│                                                             │
│  Skills (.claude/commands/):                                │
│    /ll-create → Agent 引导创建 task（含 instruction）         │
│    /ll-run    → 执行当前轮 ready stages + 引导下一步          │
└─────────────────────────────────────────────────────────────┘
```

## 4. 两层分工

```
┌──────────────────────┬───────────────────────────────────────┐
│  ll-chain CLI        │  无状态，纯文件操作                    │
│  (薄工具)            │  · 依赖解析 (ready_stages)            │
│                      │  · 读写 task/schema                   │
│                      │  · 拼装 stage 详情给 Agent             │
├──────────────────────┼───────────────────────────────────────┤
│  Agent               │  流程编排 + 实际执行                   │
│  (/ll-run skill)     │  · 查 status，获取 ready stages       │
│                      │  · 加载两层上下文                       │
│                      │  · 顺序执行当前轮所有 ready stages     │
│                      │  · 输出结果文件 + summary.md           │
│                      │  · 更新状态，引导用户执行下一轮         │
└──────────────────────┴───────────────────────────────────────┘
```

核心原则：**CLI 不思考，只读写文件。所有决策在 Agent 侧。用户手动驱动每一轮执行。**

## 5. 执行模型

### 5.1 用户驱动模型

用户通过 `/ll-run` 手动驱动每一轮 DAG 执行。每次调用执行当前所有 ready stages，完成后引导用户触发下一轮。

```
┌──────────────────────────────────────────────────────────────┐
│  用户手动驱动循环                                              │
│                                                              │
│   /ll-run A                                                  │
│     │                                                        │
│     ├─ ll-chain status A  ──▶  获取 ready_stages             │
│     │                                                        │
│     ├─ 顺序执行每个 ready stage:                              │
│     │    ll-chain update A {node} running                    │
│     │    ll-chain stage A {node}  → 获取 context             │
│     │    加载上下文 → 执行任务 → 输出结果                      │
│     │    ll-chain update A {node} completed/failed           │
│     │                                                        │
│     └─ 输出引导: "执行 /ll-run A 继续下一阶段"                │
│                                                              │
│   用户查看结果，手动执行 /ll-run A → 下一轮                    │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 DAG 执行

Flow 是一个有向无环图（DAG），Node 通过 `depends_on` 声明依赖。CLI 负责计算 `ready_stages`（所有依赖已完成的 pending 节点）。

```
    ┌──────────┐     ┌──────────┐
    │ analyze  │     │ security │     ← 无依赖，可并行
    └────┬─────┘     └────┬─────┘
         │                │
         └───────┬────────┘
                 ▼
           ┌──────────┐
           │  report  │               ← depends_on: [analyze, security]
           └──────────┘
```

### 5.3 状态流转

```
Stage 状态:   pending → running → completed
                             └→ failed → (用户介入)

Task 状态:    pending → running → completed
                             └→ failed (任一 stage failed)
```

- 任一 stage failed → task 状态变为 failed → 停止执行 → 等待用户介入
- 所有 stage completed → task 状态变为 completed
- 不考虑自动重试，失败即停

### 5.4 并行 Task

不同 task 在不同 Agent 会话中独立执行，无嵌套：

```
Agent 会话 1 → 执行 task A → .llchain/A/
Agent 会话 2 → 执行 task B → .llchain/B/
```

## 6. 数据模型

### 6.1 文件布局

```
.llchain/
├── config.yaml                  ← 全局配置
├── schemas/                     ← Flow 定义模板（用户编写）
│     └── code-review.yaml
├── A/                           ← Task 实例
│     ├── task.yaml              ← 运行状态（CLI 维护）
│     ├── stage-analyze/
│     │     ├── summary.md       ← 必须产出
│     │     ├── detail-report.md
│     │     └── metrics.json
│     ├── stage-security/
│     │     ├── summary.md       ← 必须产出
│     │     └── findings.md
│     └── stage-report/
│           ├── summary.md       ← 必须产出
│           └── final-report.md
└── B/                           ← 另一个 Task 实例
```

### 6.2 全局配置

```yaml
# .llchain/config.yaml
constraints:
  - "使用中文输出所有报告"
  - "单个任务输出不超过 20K 字符"
  - "遵循项目现有代码风格"
default_flow_id: code-review     # 可选，/ll-create Skill 优先使用
```

### 6.3 Schema（Flow 定义模板）

```yaml
# .llchain/schemas/code-review.yaml
id: code-review
description: "代码审查流程"

nodes:
  - id: analyze
    prompt: "分析代码质量，重点关注复杂度和命名规范"
    context:
      files:
        - "src/**/*.py"

  - id: security
    prompt: "进行安全审查，检查 OWASP Top 10"
    context:
      files:
        - "src/**/*.py"

  - id: report
    prompt: "综合分析结果和安全审查，生成最终报告"
    depends_on: [analyze, security]
```

- `prompt` 是纯文本，无模板变量
- DAG 通过 `depends_on` 描述

### 6.4 Task（运行状态）

```yaml
# .llchain/A/task.yaml
name: A
flow: code-review
status: running          # pending | running | failed | completed
created_at: 2026-02-28T10:00:00
instruction: "分析 src/auth/ 的认证模块代码质量"  # 可选，用户业务说明
stages:
  analyze:
    status: completed
    started_at: 2026-02-28T10:00:00
    completed_at: 2026-02-28T10:02:15
  security:
    status: completed
    started_at: 2026-02-28T10:00:00
    completed_at: 2026-02-28T10:03:40
  report:
    status: running
    started_at: 2026-02-28T10:05:00
```

- `instruction` 是可选字段，创建 task 时通过 `--instruction` 参数传入
- 当存在 instruction 时，DAG 入口节点（无 `depends_on`）的 stage context 会包含该信息

## 7. 两层 Context 模型

Agent 执行 stage 任务时，需要加载两层上下文：

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Global Constraints (全局限制)                       │
│                                                             │
│   来源: config.yaml                                         │
│   内容: "中文输出", "不超过 20K" 等硬约束                     │
│   由 CLI stage 命令返回                                      │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Dependency Context (依赖上下文)                     │
│                                                             │
│   来源: depends_on 节点的 summary.md                         │
│   内容: 上游节点的关键产出摘要                                │
│   CLI 返回路径，Agent 自己读取                                │
└─────────────────────────────────────────────────────────────┘
```

### 7.1 summary.md

每个 stage 执行完成后 **必须** 在 output_dir 下生成 `summary.md`，作为下游依赖节点的上下文输入。

- **格式不限**，Agent 根据任务性质自主决定内容和结构
- **唯一硬约束**：文件必须存在
- 下游节点默认只读 summary.md，如需详细内容可自行读取 output_dir 中的其他文件

### 7.2 CLI `stage` 命令返回结构

Agent 调用 `ll-chain stage <task> <node_id>` 获取完整任务信息。

`instruction` 字段为 `prompts` 列表结构，每项包含 `source`（来源）和 `content`（内容）：

**入口节点（无 depends_on）且 task 有 instruction：**

```yaml
node: analyze
task: A
status: pending

instruction:
  prompts:
    - source: schema
      content: "分析代码质量，重点关注复杂度和命名规范"
    - source: user
      content: "分析 src/auth/ 的认证模块代码质量"

constraints:
  - "使用中文输出所有报告"
  - "单个任务输出不超过 20K 字符"

dependencies: []
output_dir: .llchain/A/stage-analyze/
```

**非入口节点（有 depends_on）：**

```yaml
node: report
task: A
status: pending

instruction:
  prompts:
    - source: schema
      content: "综合分析结果和安全审查，生成最终报告"

# Layer 1
constraints:
  - "使用中文输出所有报告"
  - "单个任务输出不超过 20K 字符"

# Layer 2
dependencies:
  - node: analyze
    summary: .llchain/A/stage-analyze/summary.md
    output_dir: .llchain/A/stage-analyze/
  - node: security
    summary: .llchain/A/stage-security/summary.md
    output_dir: .llchain/A/stage-security/

# 输出目标
output_dir: .llchain/A/stage-report/
```

- `prompts` 始终为列表，Agent 综合所有项理解并执行任务
- `source: "schema"` 来自 Schema 模板定义，`source: "user"` 来自用户创建时的 instruction
- CLI 只返回路径，不返回文件内容。Agent 自己决定读什么、读多少

## 8. CLI 命令设计

```
ll-chain init                                # 初始化 .llchain/ + 注入 Skills
ll-chain create <task_name> --flow <id> [--instruction "..."]  # 从 flow 创建 task 实例
ll-chain list                                # 列出所有 task 实例
ll-chain status <task_name>                  # 返回 task 状态 + ready_stages
ll-chain stage <task_name> <node_id>         # 返回 stage 详情（两层 Context）
ll-chain update <task_name> <node_id> <status>  # 更新 stage 状态
ll-chain flows                               # 列出可用 schemas + default_flow
```

### 8.2 `flows` 返回结构

```yaml
flows:
  - id: code-review
    description: "代码审查流程"
  - id: refactor
    description: "重构流水线"
default_flow: code-review          # 来自 config.yaml，无配置时为 null
```

### 8.1 `status` 返回结构

CLI 计算 `ready_stages`（依赖全部满足的 pending 节点），Agent 直接使用，不需要自己做依赖解析：

```yaml
name: A
flow: code-review
status: running
ready_stages: [report]
running_stages: []
completed_stages: [analyze, security]
failed_stages: []
```

## 9. Stage 执行协议

每个 stage 在 `/ll-run` 内部按以下 4 步执行：

```
Stage 标准执行流程（/ll-run 内部）
══════════════════════════════════

1. QUERY ─── 获取任务详情
   $ ll-chain stage {task} {node_id}
   → 获得 instruction.prompts 列表 + 两层 context 路径 + output_dir

2. LOAD CONTEXT ─── 加载上下文
   ├─ 读取 constraints (全局限制，作为硬约束)
   └─ 读取各 dependency 的 summary.md
        → 如果需要更多细节，可进入 output_dir 读取

3. EXECUTE ─── 执行任务
   综合 instruction.prompts 中所有指令 + 两层 context 执行任务

4. OUTPUT ─── 输出结果 (写入 output_dir)
   ├── summary.md          ← 必须
   └── *.md / *.json       ← 其他输出（自由发挥）
```

## 10. Agent 交互流程

### 10.1 用户完整使用流程

```
用户                          Claude Code                        ll-chain CLI
─────                        ──────────                         ────────────

$ ll-chain init                                                 创建 .llchain/
                                                                注入 .claude/commands/

$ 编写 schema

方式一：Agent 引导创建（推荐）
$ claude
> /ll-create 分析 src/auth/ 的认证模块代码质量
                             $ ll-chain flows ─────────────▶    返回可用 flows
                             AI 选择 flow + 生成 task name
                             $ ll-chain create A                创建 .llchain/A/
                               --flow code-review               (含 instruction)
                               --instruction "分析 src/auth/..."
                             "已创建 task A，执行 /ll-run A"

方式二：手动创建
$ ll-chain create A --flow code-review                          创建 .llchain/A/
  [--instruction "分析 src/auth/ 的代码质量"]                     (instruction 可选)

第一轮：执行入口节点
$ claude
> /ll-run A
                             $ ll-chain status A ──────────▶    返回 ready_stages
                             ◀─────────────────────────────     [analyze, security]

                             ── Stage: analyze ──
                             $ ll-chain update A analyze running
                             $ ll-chain stage A analyze ───▶    返回 context
                             读取上下文 → 执行任务 → 输出结果
                             $ ll-chain update A analyze completed

                             ── Stage: security ──
                             (同理顺序执行)

                             $ ll-chain status A ──────────▶    还有后续 stages
                             "analyze, security 已完成！
                              执行 /ll-run A 继续下一阶段"

第二轮：执行依赖节点
> /ll-run A
                             $ ll-chain status A ──────────▶    返回 ready_stages
                             ◀─────────────────────────────     [report]

                             ── Stage: report ──
                             $ ll-chain update A report running
                             $ ll-chain stage A report ────▶    返回 context（含上游 summary 路径）
                             读取上游 summary.md → 执行任务 → 输出结果
                             $ ll-chain update A report completed

                             $ ll-chain status A ──────────▶    status: completed
                             "Task A 已全部完成！
                              查看 .llchain/A/ 获取结果"
```

### 10.2 Run Skill (/ll-run)

```
1. 执行 ll-chain status $ARGUMENTS 获取 task 状态
2. 判断终止条件：
   - status: completed → 提示用户 task 已完成，结束
   - status: failed → 提示用户有 failed stages，结束
   - ready_stages 为空 → 提示用户无可执行 stage，结束
3. 顺序执行所有 ready stages，对每个 stage：
   a. ll-chain update {task} {node} running
   b. ll-chain stage {task} {node} 获取任务详情
   c. 加载两层 Context（constraints + dependency summaries）
   d. 综合 instruction.prompts 中所有指令和上下文执行任务
   e. 将输出保存到 output_dir（必须包含 summary.md）
   f. ll-chain update {task} {node} completed
   g. 如果执行失败 → ll-chain update {task} {node} failed，停止，告知用户
4. 执行完当前轮后，再次 ll-chain status $ARGUMENTS 查看后续状态：
   - 全部 completed → "Task 已全部完成！查看 .llchain/{task}/"
   - 还有后续 stages → "执行 /ll-run {task} 继续下一阶段"
```

### 10.3 Create Skill (/ll-create)

```
1. 接收用户 instruction: $ARGUMENTS
2. 执行 ll-chain flows 获取可用 flow 列表
   - 有 default_flow → 直接使用
   - 无 default_flow → AI 根据 instruction 自动选择
3. AI 根据 instruction 生成 task name（英文小写+连字符）
4. 执行 ll-chain create {name} --flow {flow} --instruction "$ARGUMENTS"
5. 提示用户执行 /ll-run {name}（不自动触发）
```

## 11. 技术选型

- **语言**: Python 3.11
- **包管理**: uv
- **CLI 框架**: click
- **数据格式**: YAML（schema, task, config）
- **入口**: `ll-chain` CLI script（已在 pyproject.toml 注册）