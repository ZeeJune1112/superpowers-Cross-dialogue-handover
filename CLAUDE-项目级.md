# CLAUDE.md — 工作流规则与约束

> **CRITICAL**: 顶层强约束规则。按优先级自上而下排列，冲突时上方规则自动生效。所有指令均为强交割红线，不可绕过。

## 1. 语言与格式规范 (Language & Formatting)

- **ALWAYS**: 在生成任何 Superpowers 流程文档（包括 spec、plan、features、pitfalls、交接记录）时，正文必须使用**简体中文**。
- **NEVER**: 严禁翻译技术标识符。代码片段、类名、函数名、文件路径、Git 分支名必须保持**英文原貌**。
- *示例*：
  - **DO**: 正文用中文描述，`validateUser()` 保持英文。
  - **DON'T**: 强行翻译代码 API 或全英文书写文档正文。

---

## 2. 新窗口预热协议 (Session Initialization)

**WHEN** 新窗口启动 且 触发 `/continue-handoff` skill 时：
- **Priority**: 严格以该 skill 的定义为准。
- **Fallback**: 若 skill 不可用或 `INDEX.md` 为空，**REQUIRED** 立即扫描以下 4 个目录并在内存中构建临时索引：
  - `docs/superpowers/specs/`
  - `plans/`
  - `architecture/features/`
  - `architecture/pitfalls/`
- **Exception**: 若无前序交接或无上下文，直接跳过预热。

---

## 3. 核心交割纪律与质量门禁 (Handoff Discipline)

**WHEN** Plan 执行完毕、功能确认完成、或收到手动 `/handoff` 请求时：
1. **REQUIRED**: 必须先完整执行 `HANDOFF_PROTOCOL.md` 定义的 5 步固化流程，方可执行任何交接命令。
2. **REQUIRED**: 必须将 `docs/superpowers/` 下的所有变更作为**独立 commit** 提交，严禁与代码混淆提交。
3. **Command Scope**: `/handoff` 命令仅用于记录当前窗口的动态进度（Handoff Context）。**NEVER** 用其替代协议做长期的知识归档。
4. **Real-time Feedback**: 必须实时、透明地反馈具体步骤进度（例如：“正在执行记忆固化第 3 步...”）。**NEVER** 抢跑宣告任务结束（严禁使用“搞定了”、“已完成”等模糊字眼）。

---

## 4. 研发工作流与验证红线 (Workflow & Verification)

### Subagent-Driven Development (SDD) 收尾
- **REQUIRED**: 当所有 SDD 任务完成时，必须触发 `superpowers:finishing-a-development-branch` 执行分支收尾决策（合并/PR/保留/丢弃）。
- **NEVER**: 严禁在未完成 SDD 收尾决策时直接跳过执行 `/handoff`。

### 严格验证门禁 (Verification Gate)
- **REQUIRED**: 拟宣称“完成”、“通过”或“修复”前，必须先执行 `superpowers:verification-before-completion` 验证技能。
- **Evidence-Based Only**: 严禁模糊暗示，必须基于明确的终端输出证据进行汇报。

| ALWAYS (基于明确证据) | NEVER (严禁模糊暗示) |
| :--- | :--- |
| “测试通过 [见: 34/34 pass]” | “应该通过了” / “看起来差不多了” |
| “验证完毕 [见: build exit 0]” | 未见明确输出前宣称成功（一律视为违规） |
