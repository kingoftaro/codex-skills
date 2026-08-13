# Deliver Code Change

[English](https://github.com/kingoftaro/deliver-code-change/blob/main/README.en.md)

一个面向现有代码仓库的风险感知单步执行 skill。它负责实现并验证一个已经界定的代码改动，既可独立处理普通 bug 或功能调整，也可执行 `phase-step-planner` 生成并冻结的当前 STEP。

## 核心理念

不是所有改动都应走相同的重型流水线。这个 skill 在一个明确边界内，根据不确定性、影响范围和操作风险选择执行深度：小而明确的修复快速完成；跨模块变化进行简短规划和验证；涉及权限、金额、迁移或外部副作用的改动则启用更严格的控制。

它强调最小且完整的改动：优先复用现有实现、标准库和已安装依赖，避免无关重构、流程文件膨胀和未经授权的副作用。

大型阶段的拆分、状态维护和步骤验收由 `phase-step-planner` 负责；本 skill 只执行当前有界步骤，并把代码与验证证据交回规划器。

## 适用场景

- 修复 bug
- 新增或调整一个边界明确的功能
- 重构已有代码
- 修改接口、类型、配置或数据结构
- 执行已经拆分好的迁移、外部 API 或运行环境改动步骤
- 实现 `phase-step-planner` 当前验证通过的 `STEP_*.md`

调用示例：

```text
Use $deliver-code-change to implement and verify this bounded code change without expanding its approved scope.
```

## 三条执行路径

| 路径 | 适用情况 | 最低执行深度 |
|---|---|---|
| Fast | 需求明确、局部、低风险且容易回滚 | 定位、最小修改、针对性验证 |
| Standard | 跨文件行为、接口变化或存在明显不确定性 | 简短计划、检查调用方、静态检查与测试 |
| High-risk | 权限、金额、迁移、状态机、并发、外部 API、运维或破坏性行为 | 明确契约与恢复策略、分步实现、风险专项验证 |

风险优先于改动大小：即使只有一行代码，鉴权和金额逻辑也属于 High-risk。

## 工作方式

1. 读取仓库规则、项目配置、CI 和当前工作区状态。
2. 判断是独立改动，还是由 phase STATUS 与 STEP 管理的当前步骤。
3. 校验任务边界、STEP checkpoint、验收证据和需要额外授权的操作。
4. 选择 Fast、Standard 或 High-risk 路径。
5. 按需读取实现、验证和对应语言工具链参考。
6. 以最小且兼容的 diff 实现改动。
7. 使用项目已有命令验证，并如实区分 PASS、FAIL、BLOCKED 和 NOT_APPLICABLE。
8. 汇报边界遵守情况、改动和验证证据；phase-managed 模式下不自行更新 STATUS 或验收结果。

默认不创建过程日志或状态文件。存在 phase `STATUS.md` 时绝不创建第二份任务状态；只有独立且容易中断的任务才考虑单个持久化状态文件。

## 安全边界

本 skill 不会自动：

- 安装依赖
- 初始化 OpenSpec 或其他规格系统
- 提交、推送、发布或部署
- 删除文件、执行数据迁移或修改远程服务
- 把无法执行的测试说成通过

这些操作需要用户明确授权。无法运行的验证会标记为 `BLOCKED`，并与替代证据分开说明。

## 目录说明

```text
deliver-code-change/
├── SKILL.md                 # 总控：路由、授权边界和交付流程
├── agents/openai.yaml       # Codex UI 元数据
├── references/              # 按需读取的规划、风险、验证和工具链指南
└── scripts/                 # 项目检测、状态管理、契约检查和结构校验
```

关键文件：

- `references/routing.md`：Fast、Standard、High-risk 的分流规则。
- `references/phase-handoff.md`：消费 phase STATUS 与 STEP 的校验、执行和证据交接规则。
- `references/risk-controls.md`：鉴权、金额、迁移、并发、外部系统和运维的专项控制。
- `references/verification.md`：验证强度与证据标准。
- `scripts/detect_project.py`：只读识别项目语言、CI、工具与指令文件。
- `scripts/manage_state.py`：以原子方式维护可恢复的任务状态。
- `scripts/check_python_contracts.py`：检查结构化 Python 接口契约，空契约不会误报通过。

## 自检

使用 Python 标准库自检 skill 结构、相对链接、UI 元数据和脚本语法：

```text
python scripts/validate_skill.py
```

用于 Python 结构契约检查的 JSON 格式和示例见 `references/contract-format.md`。
