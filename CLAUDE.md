## 预热协议（新窗口启动时）

新窗口通过 `/continue-handoff` 命令触发状态恢复。continue-handoff 技能执行时，必须首先通过项目知识索引重建上下文：

1. 读取 `docs/superpowers/architecture/INDEX.md`
2. 按索引表格逐条读取指向的 specs、plans、features、pitfalls 文档
3. 再提取 plan 中的 Handoff Context 恢复任务状态

**兜底顺序**（INDEX.md 不存在或为空时）：
1. 扫描 `docs/superpowers/specs/`、`plans/`、`architecture/features/`、`architecture/pitfalls/` 目录
2. 若目录中存在文件 → **逐个读取**所有文件内容（不是仅列出文件名），在内存中构建临时索引
3. 若所有目录均为空 → 项目尚无已固化知识，跳过预热，依赖 handoff 传递的上下文继续工作

注：首个窗口（未执行过 continue-handoff）无需预热，直接开始工作。

## 核心交割纪律（研发红线）

- **交棒前置动作**：在当前 Superpowers 规划流（Plan）结束时，必须先读取并完整执行 `docs/superpowers/architecture/HANDOFF_PROTOCOL.md` 中定义的记忆固化协议。
- **交棒硬约束**：HANDOFF_PROTOCOL 未执行完毕前，**禁止**执行 `/handoff` 命令。如果用户在 HANDOFF_PROTOCOL 完成前请求 `/handoff`，AI 必须先行拦截，告知用户"记忆固化尚未完成"，先执行 HANDOFF_PROTOCOL 的 5 个步骤，然后再执行 /handoff。
- **严禁抢跑**：未完成上述协议前，绝对禁止向用户宣告任务结束。
- **提交责任**：HANDOFF_PROTOCOL 执行完后，必须将 `docs/superpowers/` 目录的变更提交到 Git（独立 commit），确保知识固化结果持久化到仓库。
