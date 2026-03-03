## ADDED Requirements

### Requirement: 所有 stage 携带用户 instruction
`build_stage_context` 组装 instruction 时，若 task 存在 user instruction，须对所有 stage（不论是否为入口节点）都将其加入 prompts 列表。

#### Scenario: 有依赖的节点包含用户 instruction
- **WHEN** 节点有 `depends_on` 且 task 有 user instruction
- **THEN** 该节点的 `instruction.prompts` 列表须包含 `{"source": "user", "content": "<instruction>"}`

#### Scenario: 入口节点仍包含用户 instruction
- **WHEN** 节点无 `depends_on` 且 task 有 user instruction
- **THEN** 该节点的 `instruction.prompts` 列表须包含 `{"source": "user", "content": "<instruction>"`（行为不变）

#### Scenario: task 无 user instruction
- **WHEN** task 的 instruction 字段为 None
- **THEN** 所有节点的 `instruction.prompts` 列表仅包含 schema prompt，不包含 user 来源的 prompt

### Requirement: status 命令输出包含 instruction
`status` 命令的输出中须包含 task 的 `instruction` 字段信息。

#### Scenario: task 有 instruction
- **WHEN** 查询的 task 存在 instruction
- **THEN** `status` 命令输出中包含 `instruction` 字段

#### Scenario: task 无 instruction
- **WHEN** 查询的 task 无 instruction（为 None）
- **THEN** `status` 命令输出中不包含 `instruction` 字段
