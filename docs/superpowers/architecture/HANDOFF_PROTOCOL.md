# Superpowers 跨窗口记忆固化协议

本协议解决两个问题：
1. **固化**：当前窗口的确定性知识（规划产出、功能成果、踩坑经验）在关闭前落盘
2. **预热**：新窗口启动时通过 `/continue-handoff` 快速加载这些知识，避免重复踩坑

> **四层关系**：
> - CLAUDE.md ──指向──→ 本文件（写入知识） + INDEX.md（读取知识）
> - 本文件 ──更新──→ INDEX.md
> - `/continue-handoff` skill ──读取──→ INDEX.md（预热入口）
> - `/handoff` skill ──写入──→ plan 的 Handoff Context（动态状态交接，与本协议互补）
>
> 本协议负责**确定性知识**（features、pitfalls、INDEX.md），/handoff 负责**动态状态**（当前进度、待办队列）。两者各司其职、缺一不可。

---

## 0. 环境检测与初始化

### 环境检测

| 检测方式 | 命令 | 结果 |
|----------|------|------|
| Git 仓库 | `git rev-parse --is-inside-work-tree` | 输出 `true` → 走 Git 流程 |
| 非 Git | 命令失败 | 走非 Git 流程 |

两种流程的区别仅在第 1 步（审查改动范围）和第 4 步（Git 提交），其余步骤完全相同。

### 首次使用初始化

以下条件按需创建，缺失任何一项都**不阻塞流程**——创建即可继续：

| 检查项 | 不存在时的操作 |
|--------|---------------|
| `docs/superpowers/architecture/INDEX.md` | 创建空索引文件（模板见下方） |
| `docs/superpowers/architecture/features/` 目录 | 创建目录 |
| `docs/superpowers/architecture/pitfalls/` 目录 | 创建目录 |
| `docs/superpowers/specs/` 目录 | 创建目录 |
| `docs/superpowers/plans/` 目录 | 创建目录 |

**INDEX.md 空模板**（首次初始化时写入）：

```markdown
# 项目知识索引

> 本索引在每次执行 HANDOFF_PROTOCOL 时自动更新。路径相对于 `docs/superpowers/`。

## 规划产出
| 日期 | 主题 | 文档路径 |
|------|------|----------|

## 已完成功能
| 日期 | 主题 | 文档路径 |
|------|------|----------|

## 已知坑点
| 日期 | 主题 | 文档路径 |
|------|------|----------|
```

> **注意**：目录和 INDEX.md 的创建**仅由本协议负责**。`/continue-handoff` skill 只读取已有知识，不做自动创建，避免两处初始化逻辑产生竞态。

---

## 1. 审查改动范围

### Git 流程
1. `git status --short` — 查看所有变更（含 untracked 文件）
2. `git diff --stat` — 查看已跟踪文件的改动量
3. `git diff` — 查看具体改动内容
4. 筛选：聚焦于生产代码变更、配置变更、依赖变更、文档产出（spec/plan/feature/pitfall）。忽略临时性内容（如 `console.log` 调试行、被后续 commit 覆盖的中间状态文件）

### 非 Git 流程
1. 回顾本次窗口对话中**实际创建或修改**的文件（以 Write/Edit 工具调用记录为准）
2. 回顾本次窗口中遇到的**错误和反复调试**的环节
3. 筛选：同上，聚焦确定性知识，忽略临时调试代码

---

## 2. 事务性落盘

根据第 1 步的审查结果，判断需要写入哪些分类的详细文档：

### 写入 `docs/superpowers/architecture/features/`（功能归档）
- **触发条件**：实现了新功能或重构了公共模块，且已通过测试验证
- **文件命名**：`YYYY-MM-DD-<主题>.md`
- **内容要求**：功能概述、关键设计决策、核心文件路径
- **补充功能**：若为已有功能的增量补充（如加了实时时钟），直接更新已有 feature 文档追加设计决策即可，无需新建文件

### 写入 `docs/superpowers/architecture/pitfalls/`（坑点归档）
- **触发条件**：攻克了隐蔽 Bug、配置暗坑、环境问题 **且用户明确确认要记录**
- **触发流程**：遇到问题 → 修复 → AI 主动询问"是否将此坑点写入文档？" → 用户确认 → 写入
- **文件命名**：`YYYY-MM-DD-<主题>.md`
- **内容要求**：问题现象、根因分析、确定性规避手段
- **重要**：AI 不得在未经用户确认的情况下自动创建 pitfall 文档。用户有权判断某个问题是否具有"未来会重复踩坑"的归档价值。

### 无额外落盘内容时
如果本次窗口未产生 features 或 pitfalls，跳过本步骤，直接进入第 3 步。不要为了"完成步骤"而写入低价值内容。

> **注意**：spec 和 plan 文件由 superpowers 流程（brainstorming → writing-plans）自动生成到 `specs/` 和 `plans/` 目录，不属于本步骤的落盘范围。本步骤只负责 features 和 pitfalls。

---

## 3. 更新索引（必选步骤，不可跳过）

将本次窗口的所有产出追加到 **`docs/superpowers/architecture/INDEX.md`** 的对应表格中。

### 追加规则
- 在 INDEX.md 对应分区表格的末尾追加新行
- 路径使用相对于 `docs/superpowers/` 的路径
- 追加前先检查：如果已有相同「日期 + 主题」的行，跳过不重复添加（以日期和主题的**完全匹配**为准，忽略路径大小写差异）
- 如果 INDEX.md 中对应分区表格不存在，按第 0 步的模板补齐

### 产出类型 → 索引分区映射

| 产出类型 | 写入分区 | 路径格式示例 |
|----------|----------|-------------|
| 设计规格 (spec) | `## 规划产出` | `specs/2026-05-20-foo-design.md` |
| 实现计划 (plan) | `## 规划产出` | `plans/2026-05-20-foo.md` |
| 已完成功能 (feature) | `## 已完成功能` | `architecture/features/2026-05-20-foo.md` |
| 已知坑点 (pitfall) | `## 已知坑点` | `architecture/pitfalls/2026-05-20-foo.md` |

### 追加格式示例

```markdown
| 2026-05-20 | 主题描述 | specs/2026-05-20-foo.md |
```

直接追加到对应表格最后一行数据行之后。

---

## 4. Git 提交（仅 Git 环境）

如果是 Git 仓库，必须完成以下两步：

```bash
git add docs/superpowers/
git commit -m "docs: 更新项目知识索引与架构文档（HANDOFF_PROTOCOL）"
```

非 Git 环境跳过此步。

**重要**：仅 `git add` 而不 `git commit` 会导致知识固化结果在窗口关闭后丢失。必须完成 commit。

---

## 5. 退出宣告

完成上述步骤后，向用户回复：

> 当前窗口的架构沉淀与防呆经验已安全落盘并提交。您现在可以执行 `/handoff` 命令进行状态交接。

---

## 6. 遗漏检测机制（供 /continue-handoff 使用）

本协议是否已执行，通过 INDEX.md 与实际文件的差距来判断（不使用专用标记文件）：

```
specs/ 或 plans/ 目录存在 .md 文件
  AND
INDEX.md「规划产出」表中缺少这些文件的条目
  →
上次窗口的 HANDOFF_PROTOCOL 被跳过
  →
/continue-handoff 触发回溯执行（补全 INDEX.md 索引）
```

如果缺失的是 feature/pitfall 文档本身（不只是索引条目），`/continue-handoff` 在初始化报告中标注 `(Missing Docs)` 提醒用户——这些文档包含上下文相关的设计决策，只有当时的窗口能撰写。

---

## 附：与其他组件的职责边界

| 组件 | 职责 | 触发时机 |
|------|------|---------|
| 本协议 (HANDOFF_PROTOCOL) | 确定性知识固化（features/pitfalls + INDEX.md + Git commit） | Plan 执行完毕、功能确认完成时 |
| `/handoff` skill | 动态状态交接（当前进度写入 plan 的 Handoff Context） | 窗口关闭前（需先完成本协议） |
| `/continue-handoff` skill | 新窗口预热（读取 INDEX.md + plan 恢复上下文） | 新窗口启动时 |
| CLAUDE.md | 入口规则（定义预热协议 + 交割纪律 + 语言约定） | 始终生效 |

详细预热流程见 `/continue-handoff` skill 定义文件，此处不再重复。
