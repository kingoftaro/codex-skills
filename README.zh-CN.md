# Codex Skills

[English](README.md)

这是一个面向 Codex 的软件交付 skills 集合。仓库将“大型阶段规划”和“单个有界改动执行”分开，让跨阶段、跨会话或跨模型的工作可以依据仓库证据拆分、实施和验收，而不依赖聊天记录。

## Skills

| Skill | 职责 | 适用场景 |
|---|---|---|
| [`phase-step-planner`](phase-step-planner/) | 审计大型阶段、拆分可独立验收的步骤、维护单一状态快照并准备安全交接 | 工作跨越多个验收门、会话或实施模型 |
| [`deliver-code-change`](deliver-code-change/) | 实现、验证并交付一个有界代码改动 | 行为、消费者、不确定性或验证深度值得启用专门流程，或者当前 phase STEP 已可执行 |

## 协作方式

```text
微小、局部、低风险修改
  -> 直接遵循仓库规则完成

phase-step-planner
  -> 审计仓库证据
  -> 冻结当前 STEP 及其 checkpoint

deliver-code-change
  -> 校验交接
  -> 只实现当前有界 STEP
  -> 返回代码和验证证据

phase-step-planner
  -> 根据仓库证据验收或拒绝
  -> 更新 STATUS 并准备下一 STEP
```

微小、局部、低风险修改应直接遵循适用的仓库规则完成，不加载 skill，
也不创建流程文档。一个有界改动只有在行为、消费者、不确定性或验证深度
值得启用专门实施流程时才使用 `deliver-code-change`。多阶段工作应先使用
`phase-step-planner`，然后一次执行并验收一个步骤。

风险按实际影响判断，不因出现重试、状态机等词汇自动升级。一个 STEP 通常
包含实现、必要调用方和相关测试，优先使用模块范围加明确禁区；只有独立
验收、风险或回滚边界需要时才拆分。

保留 schema `1` 和 SHA-256 checkpoint。哈希只标识正式交接时审查过的 STEP
文档版本，预期的实现 diff 不会让合同失效。在交接、新执行者接手或恢复会话、
相关材料变化以及项目明确要求的门禁处复查。

## 仓库结构

```text
codex-skills/
├── deliver-code-change/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
└── phase-step-planner/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
```

每个 skill 都是独立单元，只需安装你需要的目录。

## 安装

克隆仓库：

```powershell
git clone https://github.com/kingoftaro/codex-skills.git
```

在 Windows 中安装到个人 Codex skills 目录：

```powershell
Copy-Item -Recurse .\codex-skills\deliver-code-change "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse .\codex-skills\phase-step-planner "$env:USERPROFILE\.codex\skills\"
```

如果已经存在同名 skill，请先检查差异再替换。

## 使用示例

实现一个非琐碎的有界改动：

```text
Use $deliver-code-change for this non-trivial bounded code change; implement and verify it without expanding scope.
```

规划或恢复一个大型阶段：

```text
Use $phase-step-planner to audit this multi-stage phase and prepare one bounded executable step.
```

## 验证

先选择显式 Python 解释器，不依赖 `PATH`：

```powershell
$SkillsPython = 'C:\absolute\path\to\python.exe'
```

使用 Python 标准库验证两个 skill：

```powershell
& $SkillsPython .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
& $SkillsPython .\deliver-code-change\scripts\validate_skill.py .\phase-step-planner
```

运行验证器和恢复状态管理的隔离测试：

```powershell
Push-Location .\phase-step-planner\scripts
& $SkillsPython -B -m unittest -v test_validate_phase_artifacts.py test_validate_handoff_contract.py
Pop-Location
Push-Location .\deliver-code-change\scripts
& $SkillsPython -B -m unittest -v test_manage_state.py test_validate_skill.py
Pop-Location
```

验证生成的 phase 文档：

```powershell
& $SkillsPython .\phase-step-planner\scripts\validate_phase_artifacts.py <phase-directory>
```

默认仅检查 STATUS、索引和当前 STEP；添加 `--check-all-docs` 可查看全目录
文档卫生警告。CLI 区分结构错误 `FAIL`、待同步 `STALE` 和已记录冲突
`BLOCKED`；三者均返回退出码 `1`，不可执行。变更来源和语义冲突由 planner
判断，验证器不会刷新 checkpoint 或修改 STATUS。

验证跨 skill 的资源、模板结构与对抗性测试夹具：

```powershell
& $SkillsPython .\phase-step-planner\scripts\validate_handoff_contract.py
```

这些验证和测试只使用本地文件，不需要网络访问。随附的阶段验证器返回
`PASS`，只能证明结构与内部一致性，不能替代语义复审或绑定实时仓库状态的
项目本地验证器。
跨 skill 的措辞提示降为警告，同义改写不会使检查失败。资源缺失、引用损坏、
模板结构错误和夹具失败仍是错误。两个验证器均不证明代码质量或提供授权；
明确要求的验收条件仍须满足，不因问题严重级别较低而免除。

## 设计原则

- 仓库证据优先于模型总结和陈旧报告。
- 使用与不确定性和风险匹配的最小流程；微小修改不需要 skill。
- 每次只实现一个有界结果。
- 连续修复回归应触发根因审查，而不是自动增加 STEP。
- 文件范围和外部副作用必须明确。
- 自动化测试必须隔离浏览器、进程、通知、网络和真实用户数据副作用。
- 验证结果只使用 `PASS`、`FAIL`、`BLOCKED` 或 `NOT_APPLICABLE`，不把弱证据升级成通过。
- 提交、推送、部署、安装、迁移、删除和远程修改需要相应授权。
