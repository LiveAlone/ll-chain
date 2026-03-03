## Why

当前 `/ll-run` 命令每轮只执行当前 ready stages，执行完后需要用户手动再次调用 `/ll-run` 来触发下一轮。对于不需要中间人工干预的流水线，这种交互方式过于繁琐。需要一个"快进"（fast-forward）模式，能够自动循环执行所有阶段直到完成或失败。

## What Changes

- 新增 `ll-ff.md` 模板文件，作为 `/ll-ff` skill 的指令文件
- 该模板基于 `ll-run.md`，步骤 0-2 完全相同
- 步骤 3 改为自动循环：执行完当前轮 ready stages 后，自动查询下一轮状态并继续执行，无需用户手动触发
- 遇到失败立即终止，不继续后续阶段
- `init` 命令会将 `ll-ff.md` 一并复制到 `.claude/commands/`

## Capabilities

### New Capabilities
- `ll-ff-template`: 新增 ll-ff.md 模板文件，定义全自动快进执行协议（步骤 3 替换为自动循环逻辑）

### Modified Capabilities

## Impact

- `src/ll_chain/templates/` 目录新增 `ll-ff.md` 文件
- `init` 命令需要同步将新模板复制到 `.claude/commands/`（现有逻辑已支持自动复制所有 `.md` 模板，无需改代码）