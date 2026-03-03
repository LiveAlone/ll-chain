## ADDED Requirements

### Requirement: summary.md 作为 output_dir 文件索引
每个 stage 执行完毕后生成的 `summary.md` 须仅包含 `output_dir` 下生成文件的索引信息，不包含额外说明、执行过程描述或分析内容。

#### Scenario: 标准 summary 输出
- **WHEN** stage 执行完毕，需要生成 `summary.md`
- **THEN** `summary.md` 仅列出 `output_dir` 中每个生成文件的相对路径及一句话功能说明，格式为列表项

#### Scenario: 单文件输出
- **WHEN** stage 仅生成了 summary.md 本身（无其他额外输出文件）
- **THEN** `summary.md` 须说明本 stage 的核心产出已包含在 summary.md 中，并简要描述内容
