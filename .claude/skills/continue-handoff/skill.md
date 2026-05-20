---
name: continue-handoff
description: >-
  状态恢复协议，用于在新窗口中快速重建上下文。当用户在对话中输入指令 /continue-handoff 时触发。
---

# Skill: Resume Protocol (状态恢复协议)

> **Version**: 1.4
> **配合协议**: 需与 `Handoff Protocol` 配合使用，用于在新窗口中快速重建上下文。

## 触发条件

当用户在对话中输入指令 `/continue-handoff`，或发送类似“继续执行”、“请阅读 plan 中的 Handoff Context 并继续执行”、“恢复状态”等指令时，必须优先执行此协议。

## 执行动作 (严格按序执行)

一旦触发，你必须主动从项目规划文件中提取状态，并预热工作区。请严格按以下步骤操作：

### 0. 索引预热（前置步骤，不可跳过）

在挂载 Plan 文件之前，必须先通过项目知识索引重建全局上下文：

- 读取 `docs/superpowers/architecture/INDEX.md`
- 若 INDEX.md 存在且有数据行 → 按「规划产出」「已完成功能」「已知坑点」三个分区表格，逐条读取所有指向的文档
- 若 INDEX.md 不存在或无数据行 → 扫描 `docs/superpowers/specs/`、`plans/`、`architecture/features/`、`architecture/pitfalls/` 四个目录，**逐个读取**目录中所有 .md 文件（不是仅列出文件名）
- 若以上目录也均为空 → 项目尚无已固化知识，跳过本步骤，直接进入第 1 步

**基础设施自举**：目录和 INDEX.md 的创建由 HANDOFF_PROTOCOL 第 0 步统一负责。本步骤仅负责读取已有知识；若目录缺失，在初始化报告中标注 `(Missing Dirs)`，不做自动创建——避免与 HANDOFF_PROTOCOL 的初始化逻辑产生竞态。

**遗漏检测与回溯执行（关键自愈机制）**：
在读取完 INDEX.md 和四个目录的实际文件后，执行以下比对：

1. 若 `specs/` 或 `plans/` 目录存在 .md 文件，但 INDEX.md「规划产出」表中缺少这些文件的条目 → 上次窗口的 HANDOFF_PROTOCOL **被跳过了**
2. 若 `architecture/features/` 或 `architecture/pitfalls/` 目录存在 .md 文件，但 INDEX.md「已完成功能」或「已知坑点」表中缺少对应条目 → 上次窗口 HANDOFF_PROTOCOL **未完成全部步骤**

**回溯执行**（检测到遗漏时立即执行）：
a. 将未被索引的 specs、plans、features、pitfalls 文件逐一追加到 INDEX.md 对应分区表
b. 若 INDEX.md 不存在 → 按 HANDOFF_PROTOCOL 第 0 步模板创建
c. git add docs/superpowers/ && git commit -m "docs: 回溯补全遗漏的知识索引（HANDOFF_PROTOCOL 遗漏检测触发）"
d. 在初始化报告中标注 `(Retroactive HANDOFF) 检测到上次窗口遗漏了记忆固化，已自动回溯补全索引`

**注意**：回溯执行只补全 INDEX.md（确保下次可以按索引读取），不会为上次窗口自动创建 feature/pitfall 文档——这些只能由当时的窗口基于上下文撰写。如果缺失的是 feature/pitfall 文档本身，在初始化报告中标注 `(Missing Docs)` 提醒用户。

**注意**：本步骤的目的是在新窗口中快速恢复项目全貌，不只是恢复当前任务上下文。读取到的历史 specs、features、pitfalls 可以帮助你理解项目背景和避免重复踩坑。

### 1. 挂载 Plan 文件

静默读取项目中的规划文件。

- 优先读取用户在指令中明确提供的路径（如 `@docs/superpowers/plans/xxx.md`）。
- 若未指定，则扫描 `docs/superpowers/plans` 目录，**优先选择最近修改时间最新的 .md 文件**（与 /handoff 的 fallback 策略一致）。
- **路径解析规则**：若当前处于 git worktree 中，以 worktree 的根目录为基准扫描；否则以当前工作目录为基准。
- 如果找不到任何带有交接记录的文件，向用户报错："未找到有效的 plan 文件或交接记录，请确认路径。"

### 2. 提取并解析上下文

在文件中定位到 `## Handoff Context (交接上下文)` 节点。

- 若文件存在但不含该节点，向用户报错："plan 文件中未找到 Handoff Context 节点，请确认是否已执行过 /handoff 交接。"
- **通过 `Record #N` 编号识别最新记录**：选取编号最大的记录（非按位置判断），忽略历史旧记录。
- **分支校验**：读取记录中的 `Git Branch` 字段，与当前 git 分支对比。若不匹配，在初始化报告中警告用户，但不阻断流程。
- 提取出 `Current Focus`、`Last Action`、`Architecture & Dependencies`、`Blockers & Logs` 以及 `Pending Queue & Next Step` 的具体内容。

### 3. 工作区深度预热 (关键步骤)

不要仅仅是复述交接内容，你必须通过工具**主动读取**相关文件以恢复完整的代码记忆：

- **读取目标文件**：根据 `Last Action` 中最后修改的脚本，以及 `Next Step` 中指示需要阅读的文件，立即在后台使用文件读取工具查看这些文件的最新代码。若文件已不存在（被删除或重命名），跳过该文件并在结束响应中提示用户，不中断整体流程。
- **过期上下文检测**：读取文件后，对比文件实际内容与 `Last Action` 中的描述。如果文件内容与描述严重不匹配（如类名/函数名完全不同、文件结构大幅重构），在初始化报告中标注 `(Stale Context)` 并建议用户确认当前状态后再继续。
- **Plan 完整性校验**：对比 plan 文件中的任务列表与 `Pending Queue` 描述。如果任务数量或描述存在明显差异（如 Pending Queue 引用了 plan 中不存在的任务），在初始化报告中标注 `(Plan Modified)` 并提示用户。
- **校验环境规则**：认真阅读 `Architecture & Dependencies`，在接下来的代码生成中，严格遵守里面规定的依赖注入规则（如 IoC 容器注册）或异步规范。
- **分析阻碍点**：如果 `Blockers & Logs` 包含 `(Blocking)` 级别的报错，准备将解决该报错作为首要任务。

### 4. 状态校验

对比读取到的实际代码文件与 `Last Action` 中的状态标注。例如，如果标注为 `(Unverified)` 或代码中存在明显的断层，在心中做好记录，准备在下一步进行验证。

**若检测到过期上下文或 Plan 不一致**：在初始化报告中明确列出差异项，由用户决定是按原计划继续还是先同步最新状态。

## 结束响应

完成上述静默读取和预热后，请向用户输出以下结构化的初始化报告，并等待用户的执行指令：

> **上下文已恢复并预热完毕**
>
> - **当前焦点**: [提取的 Current Focus，用一句话简述]
> - **阻碍状态**: [简述有无 Bug，若有则说明是否 Blocking]
> - **已读取文件**: [列出刚才在后台预热读取过的具体文件名，如 `PlayerController.cs`]
> - **分支校验**: [当前分支 vs 记录中的分支，是否匹配]
> - **上下文状态**: [正常 / (Stale Context) 文件内容与记录不匹配 / (Plan Modified) Plan 与 Pending Queue 不一致]
>
> **下一步行动 (Next Step)**:
> [详细说明根据 Handoff 建议，接下来马上要执行的动作或编写的代码]
>
> ---
>
> *请确认是否立即开始执行上述任务？（回复”继续”或补充新要求）*
