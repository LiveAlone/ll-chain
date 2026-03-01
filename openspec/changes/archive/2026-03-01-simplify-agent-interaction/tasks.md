## 1. 重写 /ll-run Skill 模板

- [x] 1.1 重写 `src/ll_chain/templates/ll-run.md`，融合 Worker 执行逻辑，包含完整协议：查状态 → 判断终止条件 → 顺序执行 ready stages（QUERY → LOAD CONTEXT → EXECUTE → OUTPUT）→ 更新状态 → 再查状态 → 引导下一步

## 2. 删除 /ll-worker 相关代码

- [x] 2.1 删除 `src/ll_chain/templates/ll-worker.md` 模板文件
- [x] 2.2 修改 `src/ll_chain/commands/init_cmd.py` 中 `SKILL_FILES` 列表，移除 `"ll-worker.md"` 条目

## 3. 更新项目文档

- [x] 3.1 更新 `CLAUDE.md` 中架构描述：三层分工→两层分工，移除 Worker/ll-worker 相关描述，更新 /ll-run 职责说明

## 4. 验证

- [x] 4.1 运行 `uv run pytest` 确保现有测试通过（已更新引用 ll-worker.md 的测试用例，51 passed）
- [x] 4.2 在干净目录执行 `ll-chain init`，验证 `.claude/commands/` 下仅注入 `ll-run.md` 和 `ll-create.md`
