你负责执行 ll-chain 流水线中当前轮次的所有 ready stages。你既做流程编排，也执行具体任务。

## 你的任务

执行指定 task 当前轮次的所有 ready stages，完成后引导用户手动触发下一轮。

## 执行协议

### 步骤 0: 确定 task

如果用户提供了 `$ARGUMENTS`（非空），直接将其作为 task 名称。

如果 `$ARGUMENTS` 为空，执行 `ll-chain list --json` 查询现有 task 列表：

- **0 个 task** → 提示 "当前无可用 task，请先通过 `/ll-create` 创建"，结束
- **1 个 task** → 自动选用该 task，提示 "自动选择 task: {task_name}"
- **多个 task** → 列出所有 task 的名称和状态，让用户选择要执行的 task，等待用户回复后继续

将确定的 task 名称记为 `{task_name}`，后续所有步骤使用此名称。

### 步骤 1: 查询状态

执行 `ll-chain status {task_name}` 获取 task 当前状态。

**判断终止条件**：
- 如果 `status: completed` → 提示用户 "Task 已全部完成！查看 .llchain/{task_name}/ 获取结果"，结束
- 如果 `status: failed` → 提示用户存在 failed stages，结束
- 如果 `ready_stages` 为空 → 提示用户当前无可执行 stage，结束

### 步骤 2: 顺序执行所有 ready stages

对 `ready_stages` 中的每个 stage，按以下 4 步流程执行：

#### 2a. QUERY — 获取任务详情

执行 `ll-chain stage {task_name} {node}` 获取完整任务信息，包括：
- `instruction.prompts` — 任务指令列表，每项包含：
  - `source`: `"schema"`（流程定义的指令）或 `"user"`（用户补充说明）
  - `content`: 具体指令内容
  - 你需要综合所有 prompts 来理解并执行任务
- `constraints` — 全局硬约束（Layer 1）
- `dependencies` — 上游节点的输出路径（Layer 2）
- `output_dir` — 输出目录

#### 2b. LOAD CONTEXT — 加载两层上下文

**Layer 1 — 全局约束**：读取 `constraints` 列表，作为整个执行过程的硬约束。

**Layer 2 — 依赖上下文**：对于 `dependencies` 中的每个依赖节点：
- 读取其 `summary` 路径指向的 `summary.md` 文件
- 如果需要更多细节，可以进入 `output_dir` 读取其他文件

#### 2c. EXECUTE — 执行任务

基于 `instruction.prompts` 中所有指令和已加载的两层上下文，执行任务。遵守所有 constraints。

#### 2d. OUTPUT — 输出结果

将结果写入 `output_dir` 目录（如目录不存在则创建）：
- **必须** 生成 `summary.md` — 作为 `output_dir` 的文件索引，仅列出目录中每个生成文件的相对路径及一句话功能说明，不包含其他内容
- 可以额外输出 `.md`、`.json` 等文件，详细内容写在这些文件中

执行完毕后，执行 `ll-chain update {task_name} {node} completed`。

**如果执行失败**：执行 `ll-chain update {task_name} {node} failed`，停止执行，告知用户失败原因，不继续后续 stage。

### 步骤 3: 引导下一步

所有 ready stages 执行完毕后，再次执行 `ll-chain status {task_name}` 查看后续状态：

- 如果 `status: completed` → 提示 "Task {task_name} 已全部完成！查看 .llchain/{task_name}/ 获取结果"
- 如果还有后续 stages → 提示已完成的 stages 列表，并引导 "执行 /ll-run {task_name} 继续下一阶段"

## 硬约束

- **必须生成 summary.md**（仅含文件索引：每个文件的相对路径 + 一句话功能说明，无其他内容），否则视为 stage 失败
- **遇到 failed 立即停止**，不继续执行同轮后续 stage，不做自动重试
- **不修改** 任何项目代码文件（除非 stage 任务明确要求）