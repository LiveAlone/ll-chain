## 1. 新增用户级 schema 目录常量

- [x] 1.1 在 `constants.py` 中新增 `USER_SCHEMAS_DIR = Path.home() / ".local" / "share" / "llchain" / "schemas"`

## 2. flows 命令支持用户级 schema 加载

- [x] 2.1 修改 `commands/flows.py`：先扫描 `USER_SCHEMAS_DIR`（若存在），再扫描项目级 `LLCHAIN_DIR / "schemas"`，以 schema.id 为 key 去重，项目级覆盖用户级
- [x] 2.2 为 flows 命令编写单元测试：覆盖「仅项目级」「仅用户级」「同名覆盖」「用户目录不存在」四种场景

## 3. 修改 instruction 分发策略

- [x] 3.1 修改 `core/context.py` 中 `build_stage_context`：移除 `if not node.depends_on` 条件，使所有 stage 均携带 user instruction
- [x] 3.2 更新 `build_stage_context` 单元测试：验证有依赖节点也包含 user instruction，以及无 instruction 时的行为

## 4. status 命令输出 instruction

- [x] 4.1 修改 `commands/status.py`：在输出 result dict 中增加 `instruction` 字段（仅当 task.instruction 存在时）
- [x] 4.2 为 status 命令的 instruction 输出编写单元测试
