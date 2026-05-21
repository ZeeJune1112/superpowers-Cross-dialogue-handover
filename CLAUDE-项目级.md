# CLAUDE.md — 工作流规则
> 顶层强约束规则。按优先级自上而下排列，冲突时上方规则自动生效。
> 以下所有 WHEN/THEN 均不可绕过。不包含 "WHEN" 条件的规则始终生效。

## A. 语言约定
**WHEN** 生成任何 Superpowers 流程文档（spec、plan、features、pitfalls、交接记录）
**THEN** 正文必用中文；代码片段、类名、函数名、文件路径、Git 分支名必须保持英文原貌。
*   **DO**: spec 正文用中文写 / `validateUser()` 保持英文。
*   **DON'T**: 强行翻译代码命名，或用全英文书写正文。*(原因：用户母语为中文，确保文档高效流转)*

## B. 新窗口预热协议
**WHEN** 新窗口启动 且 触发 `/continue-handoff` skill
**THEN** 严格以该 skill 定义为准。CLAUDE.md 仅做以下逻辑兜底：
*   **正常流程**：skill 可用且 `INDEX.md` 非空 → 顺控执行，本文件不介入。
*   **兜底流程**：若 skill 不可用或 `INDEX.md` 为空 → 强行扫描以下 4 个目录并在内存构建临时索引：
    `docs/superpowers/specs/`、`plans/`、`architecture/features/`、`architecture/pitfalls/`
*   **首个窗口**：无前序交接，直接跳过预热。

## C. 核心交割纪律（研发红线）
**WHEN** Plan 执行完毕 / 功能确认完成 / 期间收到 `/handoff` 请求
**THEN** 必须先执行 `HANDOFF_PROTOCOL.md`（5步固化）并将 `docs/superpowers/` 变更以**独立 commit** 提交，方可执行 `/handoff`。

| DO | DON'T |
|---|---|
| 未完时拦截 `/handoff` 并提示 "记忆固化尚未完成" → 引导执行协议 | 未完协议时直接响应 `/handoff` 写入，或混淆提交文档代码 |
| 用 `/handoff` 仅记录当前窗口的动态进度（Handoff Context） | 用 `/handoff` 替代协议做知识归档 |
| 实时反馈真实进度（如："正在执行记忆固化第 3 步..."） | 抢跑宣告任务结束（严禁说 "任务已完成！" / "搞定了！"） |

## D. 工作流完整性
*   **SDD 收尾红线**：WHEN `subagent-driven-development` 任务全完 → THEN 必先触发 `superpowers:finishing-a-development-branch` 执行收尾决策（合并/PR/保留/丢弃），严禁直跳 `/handoff`。
*   **验证红线**：WHEN 拟宣称 "完成/通过/没问题" → THEN 必先执行 `superpowers:verification-before-completion` 验证。

| DO (基于明确证据) | DON'T (严禁模糊暗示) |
|---|---|
| "测试通过 [见: 34/34 pass]" | "应该通过了" / "看起来差不多了" |
| "验证完毕 [见: build exit 0]" | 未见明确输出前宣称成功（一律视为违规） |
