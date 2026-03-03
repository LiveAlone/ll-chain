## Context

当前 `ll-run.md` skill 模板硬编码了 `$ARGUMENTS` 作为 task 名称，要求用户每次执行 `/ll-run <task_name>` 时必须传入参数。实际使用中，大部分场景只有一个活跃 task，手动输入 task 名称增加了不必要的操作步骤。

此外，`summary.md` 的输出规范过于宽松（"必须生成 summary.md"+"可以额外输出"），导致 Agent 倾向于生成冗长内容，影响下游节点加载效率。

## Goals / Non-Goals

**Goals:**
- 用户执行 `/ll-run` 时无需手动传入 task 名称，通过智能推断自动确定
- `summary.md` 有明确的格式约束，仅作为 `output_dir` 的文件索引

**Non-Goals:**
- 不修改 CLI 代码（`list`、`status` 等命令保持不变）
- 不改变 ll-chain 的核心工作流（DAG 执行、状态流转等）

## Decisions

### 决策 1：task 推断逻辑放在 skill 模板中

**选择**：在 `ll-run.md` 模板的步骤 1 前新增"步骤 0: 确定 task"，利用 `ll-chain list --json` 的输出进行判断。

**理由**：
- 遵循"CLI 不思考，Agent 做决策"的架构原则
- 无需新增 CLI 命令或参数，零代码变更
- 备选方案（CLI 新增 `--auto` flag）违反了薄工具设计理念

### 决策 2：summary.md 定位为文件索引

**选择**：在模板的 OUTPUT 步骤中明确 summary.md 的格式：列出 `output_dir` 下每个生成文件的路径和一句话功能说明。

**理由**：
- 下游节点需要的是"哪些文件可用"而非"执行过程的叙述"
- 精简的索引格式便于 Agent 快速定位所需信息
- 若需详细内容，Agent 可直接读取对应文件

## Risks / Trade-offs

- [无 task 时的引导体验] → 模板中明确给出 `ll-chain create` 的引导提示，保持用户知道下一步操作
- [多 task 选择的交互方式] → 依赖 Agent 自身的对话能力列出选项让用户选择，不同 Agent 体验可能略有差异
