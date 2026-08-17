# Codex Skills

[English](./README.md) | 简体中文

一组专注于软件变更规划与交付的 Codex skills，通过明确的工作边界、仓库证据和可验证的交接机制，提高复杂开发工作的可靠性。

本仓库包含两个相互配合的 skill：

| Skill | 职责 | 适用场景 |
|---|---|---|
| [`phase-step-planner`](./phase-step-planner/) | 审计大型软件阶段，并将其拆分为边界明确、可独立验证的实施步骤 | 工作横跨多个验收关卡、会话或实施模型 |
| [`deliver-code-change`](./deliver-code-change/) | 在不擅自扩大范围的前提下，实施并验证一项有明确边界的代码变更 | Bug 修复、功能调整、重构、接口变更、迁移步骤或已确认的阶段步骤可以开始实施 |

## 两个 skill 如何协作

```text
phase-step-planner
  -> 审计仓库证据
  -> 核对计划、代码、迁移、测试和保留证据
  -> 定义当前唯一可执行步骤

deliver-code-change
  -> 验证交接内容
  -> 预演副作用边界和测试隔离方式
  -> 只实施边界内的变更
  -> 返回代码和验证证据

phase-step-planner
  -> 根据仓库证据接受或拒绝结果
  -> 更新阶段状态
  -> 准备下一个步骤
```

对于独立且边界清晰的变更，可以直接使用 `deliver-code-change`。当工作包含多个需要独立验收的结果，或需要跨会话、跨模型交接时，应先使用 `phase-step-planner`。

## 设计原则

- 仓库证据的优先级高于模型总结和过时报告。
- 每次只实施一个边界明确的结果。
- 明确记录文件范围、契约、状态转换和外部副作用。
- 自动化测试必须隔离浏览器、进程、通知、网络和真实用户数据。
- 工厂函数和只读构造器不得触发隐藏的启动副作用。
- 验证结果使用 `PASS`、`FAIL`、`BLOCKED` 或 `NOT_APPLICABLE`，不夸大较弱证据。
- 提交、推送、部署、迁移、删除和其他重要操作需要获得相应授权。

## 仓库结构

```text
codex-skills/
+-- deliver-code-change/
|   +-- SKILL.md
|   +-- agents/
|   +-- references/
|   `-- scripts/
`-- phase-step-planner/
    +-- SKILL.md
    +-- agents/
    +-- assets/
    +-- references/
    `-- scripts/
```

每个 skill 的核心职责都是自包含的：`deliver-code-change` 无需规划器也能执行独立的有界变更，`phase-step-planner` 无需执行器也能完成阶段规划与复审。当两个目录相邻安装时，规划器的 handoff validator 还会检查双方共享的 schema 契约。`SKILL.md` 是每个 skill 的入口文件；支持性参考资料仅在满足对应条件时加载。

## 安装

克隆仓库：

```powershell
git clone https://github.com/kingoftaro/codex-skills.git
cd codex-skills
```

在 Windows 上，将一个或两个 skill 目录复制到个人 Codex skills 目录：

```powershell
Copy-Item -Recurse .\deliver-code-change "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse .\phase-step-planner "$env:USERPROFILE\.codex\skills\"
```

替换已有安装前，请先检查差异。如果更新后的 skill 没有立即生效，请重启 Codex 或开启一个新任务。

## 使用方式

实施一项有明确边界的变更：

```text
使用 $deliver-code-change 实施并验证这项有明确边界的代码变更，不要扩大已批准的范围。
```

规划或继续一个大型阶段：

```text
使用 $phase-step-planner 审计当前阶段，并准备下一个有明确边界的实施步骤。
```

进行阶段交接时，应向实施模型提供适用的项目指令、阶段 `STATUS.md`、当前 `STEP_*.md`，以及明确指定的只读参考文件。

## 本地验证

这些脚本要求 Python 3.10 或更高版本，并且只使用标准库。以下示例假定 `python` 能解析到选定的解释器；否则请用该解释器的绝对路径替换它。

验证两个 skill 的结构：

```powershell
python .\deliver-code-change\scripts\validate_skill.py .\deliver-code-change
python .\deliver-code-change\scripts\validate_skill.py .\phase-step-planner
```

完成语义一致性审查后，先预检新的 schema 2 Git 交接。该命令会验证完整候选内容，但不会改写 `STATUS.md`：

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py --prepare <阶段目录> --dry-run
```

然后以原子方式把 STEP 摘要和实时 Git 快照写入 `STATUS.md`，并验证结果：

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py --prepare <阶段目录>
```

只读地重新验证现有交接：

```powershell
python .\phase-step-planner\scripts\validate_phase_artifacts.py <阶段目录>
```

准备操作会先在内存中验证候选内容；如果最终验证失败且期间没有并发编辑，则恢复原始 `STATUS.md`。schema 2 把机器事实集中保存在 `STATUS.md` 的 JSON 块中，通过摘要绑定阶段契约注册表和当前 STEP，拒绝注册表中不存在的 STEP 契约 ID，并把记录的 HEAD 与工作树指纹同实时 Git 比较。工作树指纹会排除 STATUS 和单独计算摘要的 STEP，避免自引用。非 Git 项目可使用 manual repository 模式，但必须独立比较仓库状态。

schema 2 对必需的 STEP 标题、契约 ID 和 active risk packs 使用受限 Markdown 协议；围栏代码示例不会被当作机器元数据。schema 1 自 2026-08-17 起弃用，只接收兼容性修复，并将在不早于 2026-12-01 的首次破坏性发布中移除。在移除前，CLI 校验会输出弃用警告；schema 1 保留旧式跨文档检查，但不会获得实时 Git 校验。

运行两个回归测试套件：

```powershell
python -m unittest discover .\deliver-code-change\scripts -p "test_*.py"
python -m unittest discover .\phase-step-planner\scripts -p "test_*.py"
```

验证规划器与实施器之间的交接契约：

```powershell
python .\phase-step-planner\scripts\validate_handoff_contract.py
```

当 `deliver-code-change` 与规划器相邻安装时，该命令会验证双方的集成契约；否则只验证规划器自身契约，并将执行器检查报告为 `NOT_APPLICABLE`。GitHub Actions 工作流会在 Python 3.10 和 3.13 上运行同样的检查。所有验证脚本都不会安装依赖或访问网络。

## 维护仓库

本仓库特意在同时包含两个 skill 的上级目录初始化 Git，因此两个 skill 可以共享一套历史记录，后续更新也更直接：

```powershell
git status
git diff
git add README.md README.zh-CN.md deliver-code-change phase-step-planner
git commit -m "Update Codex skills"
git push
```

发布前请检查暂存文件清单，确保生成缓存和本地配置没有进入 Git，并如实记录所有被阻塞的验证项。

## 许可证

本仓库目前尚未添加许可证。在添加许可证之前，版权归仓库所有者所有，其他人不会自动获得复用授权。
