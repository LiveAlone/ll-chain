## 1. 修改 ll-run.md — 自动推断 task

- [x] 1.1 在步骤 1 前新增"步骤 0: 确定 task"，实现以下逻辑：若 `$ARGUMENTS` 非空则直接使用；若为空则执行 `ll-chain list --json`，根据返回结果数量分三种情况处理（0 个引导创建、1 个自动选用、多个列出选择）
- [x] 1.2 将后续步骤中所有硬编码的 `$ARGUMENTS` 替换为推断出的 task 变量名（如 `{task_name}`），确保整个模板的 task 引用一致

## 2. 修改 ll-run.md — 精简 summary.md 规范

- [x] 2.1 重写步骤 2d OUTPUT 中关于 `summary.md` 的描述，明确其为 `output_dir` 文件索引格式：仅列出每个生成文件的相对路径和一句话功能说明，禁止输出额外内容
- [x] 2.2 更新"硬约束"部分中关于 summary.md 的条目，补充格式要求