# Codex Skills

[English](README.md)

这是一个面向 Codex 的软件交付 skills 集合。仓库将“大型阶段规划”和“单个有界改动执行”分开，让跨阶段、跨会话或跨模型的工作可以依据仓库证据拆分、实施和验收，而不依赖聊天记录。

## Skills

| Skill | 职责 | 适用场景 |
|---|---|---|
| [`phase-step-planner`](phase-step-planner/) | 审计大型阶段、拆分可独立验收的步骤、维护单一状态快照并准备安全交接 | 工作跨越多个验收门、会话或实施模型 |
| [`deliver-code-change`](deliver-code-change/) | 实现、验证并交付一个有界代码改动 | 已经明确的 bug 修复、功能调整、重构、接口变更或当前 phase STEP |

## 协作方式

```text
phase-step-planner
  -> 审计仓库证据
  -> 冻结当前 STEP 及其 checkpoint

deliver-code-change
  -> 校验 handoff
  -> 只实现当前有界 STEP
  -> 返回代码和验证证据

phase-step-planner
  -> 根据仓库证据验收或拒绝
  -> 更新 STATUS 并准备下一 STEP
```

独立的小型改动可以直接使用 `deliver-code-change`。多阶段工作应先使用 `phase-step-planner`，然后一次执行并验收一个步骤。

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

实现一个有界改动：

```text
Use $deliver-code-change to implement and verify this bounded code change without expanding its approved scope.
```

规划或恢复一个大型阶段：

```text
Use $phase-step-planner to audit this phase and prepare the next bounded implementation step.
```

## 验证

使用 Python 标准库验证 `deliver-code-change`：

```powershell
python .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
```

运行 `phase-step-planner` 的隔离测试：

```powershell
Push-Location .\phase-step-planner\scripts
python -m unittest -v test_validate_phase_artifacts.py
Pop-Location
```

验证生成的 phase 文档：

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py <phase-directory>
```

这些验证和测试只读取本地文件，不需要网络访问。

## 设计原则

- 仓库证据优先于模型总结和陈旧报告。
- 每次只实现一个有界结果。
- 文件范围和外部副作用必须明确。
- 自动化测试必须隔离浏览器、进程、通知、网络和真实用户数据副作用。
- 验证结果只使用 `PASS`、`FAIL`、`BLOCKED` 或 `NOT_APPLICABLE`，不把弱证据升级成通过。
- 提交、推送、部署、安装、迁移、删除和远程修改需要相应授权。
