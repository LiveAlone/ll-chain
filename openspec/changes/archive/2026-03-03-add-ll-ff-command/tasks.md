## 1. 创建 ll-ff 模板文件

- [x] 1.1 在 `src/ll_chain/templates/` 下创建 `ll-ff.md`，复制 `ll-run.md` 内容，修改开头描述和步骤 3 为自动循环逻辑（完成后自动回到步骤 1，失败立即终止，completed 时结束）
- [x] 1.2 在 `src/ll_chain/commands/init_cmd.py` 的 `SKILL_FILES` 列表中添加 `"ll-ff.md"`
