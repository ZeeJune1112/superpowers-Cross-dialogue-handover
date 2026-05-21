## 预热协议（新窗口启动时）

新窗口通过 `/continue-handoff` 触发状态恢复，其 skill 定义文件包含完整的预热逻辑（索引读取 → 遗漏检测 → Plan 挂载 → 工作区预热）。此处仅保留 CLAUDE.md 层面的兜底规则，详细步骤以 `/continue-handoff` skill 为准。

**兜底**：若 `/continue-handoff` skill 不可用或 INDEX.md 为空，扫描 `docs/superpowers/specs/`、`plans/`、`architecture/features/`、`architecture/pitfalls/` 四个目录，逐个读取所有 .md 文件在内存中构建临时索引。

注：首个窗口无需预热。

## 文档语言约定

Superpowers 流程产出的**所有文档正文**必须使用中文，包括但不限于：spec（设计规格）、plan（实现计划，含 Handoff Context 交接记录）、features（功能归档）、pitfalls（坑点归档）。代码片段、类名、函数名、文件路径、Git 分支名可保留英文。

原因：用户母语为中文，英文阅读有障碍。

## 核心交割纪律（研发红线）

- **交棒前置动作**：Plan 执行完毕、功能确认完成后，必须执行 `docs/superpowers/architecture/HANDOFF_PROTOCOL.md` 定义的记忆固化协议（5 步）。
- **交棒硬约束**：HANDOFF_PROTOCOL 未执行完毕前，**禁止**执行 `/handoff`。若用户在此期间请求 `/handoff`，AI 必须拦截并告知"记忆固化尚未完成"，先执行 HANDOFF_PROTOCOL，再执行 /handoff。
- **/handoff 用途**：将当前窗口的动态进度写入 plan 的 Handoff Context，供下个窗口恢复。**不是**知识归档工具——归档交给 HANDOFF_PROTOCOL。
- **严禁抢跑**：HANDOFF_PROTOCOL 未完成前，禁止向用户宣告任务结束。
- **提交责任**：HANDOFF_PROTOCOL 执行完后，将 `docs/superpowers/` 目录变更以独立 commit 提交到 Git，确保知识固化持久化。
