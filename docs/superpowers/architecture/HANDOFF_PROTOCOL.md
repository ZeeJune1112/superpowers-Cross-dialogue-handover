# HANDOFF_PROTOCOL — 跨窗口记忆固化协议

> **执行者**: AI
> **触发时机**: Plan 执行完毕或功能确认完成后，窗口关闭前
> **输出**: features/pitfalls 文档 + INDEX.md 更新 + Git commit（如适用）
> **协作**: `/handoff` 负责动态状态交接（写入 plan 的 Handoff Context），本协议负责确定性知识固化

---

## Step 0: 环境检测与初始化

### 0a. 检测是否为 Git 仓库

```
运行: git rev-parse --is-inside-work-tree
输出 "true" → is_git = true
命令失败 → is_git = false
```

`is_git` 影响 Step 1（审查范围）和 Step 4（提交），其余步骤不变。

### 0b. 确保以下目录和文件存在

缺失则创建，不阻塞流程：

| 路径 | 不存在时 |
|------|---------|
| `docs/superpowers/architecture/INDEX.md` | 写入下方空模板 |
| `docs/superpowers/architecture/features/` | mkdir |
| `docs/superpowers/architecture/pitfalls/` | mkdir |
| `docs/superpowers/specs/` | mkdir |
| `docs/superpowers/plans/` | mkdir |

**INDEX.md 空模板**（仅首次初始化时写入）：

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

> 注意：目录和 INDEX.md 的创建**仅由本协议负责**。`/continue-handoff` 不做自动创建，避免竞态。

---

## Step 1: 审查改动范围

### if is_git

```bash
git status --short
git diff --stat
git diff
```

### else

回顾本次对话中 Write/Edit 工具调用实际创建或修改的文件，以及遇到的错误和调试环节。

### 共同过滤规则

保留：生产代码变更、配置变更、依赖变更、文档产出（spec/plan/feature/pitfall）
忽略：临时调试代码（console.log 等）、被后续 commit 覆盖的中间状态

---

## Step 2: 事务性落盘

根据 Step 1 审查结果，判断是否需要写入 features 或 pitfalls。**无内容则跳过，直接进入 Step 3。**

### features — 写入 `docs/superpowers/architecture/features/`

- **触发条件**: 实现了新功能或重构了公共模块，且已通过测试验证
- **文件命名**: `YYYY-MM-DD-<主题>.md`
- **内容**: 功能概述、关键设计决策、核心文件路径
- **增量补充**: 若为已有功能的增量改进，直接更新已有 feature 文档追加内容，不新建文件

### pitfalls — 写入 `docs/superpowers/architecture/pitfalls/`

- **触发条件**: 攻克了隐蔽 Bug、配置暗坑、环境问题
- **前置要求**: 必须先询问用户"是否将此坑点写入文档？"，用户确认后才写入。AI 不得自动创建 pitfall 文档。
- **文件命名**: `YYYY-MM-DD-<主题>.md`
- **内容**: 问题现象、根因分析、确定性规避手段

---

## Step 3: 更新 INDEX.md

将本窗口所有产出追加到 `docs/superpowers/architecture/INDEX.md` 对应表格。**必选，不可跳过。**

### 追加规则

- 路径使用相对于 `docs/superpowers/` 的路径
- 追加前检查：已有相同「日期 + 主题」的行则跳过（以完全匹配为准，忽略路径大小写差异）
- 对应分区表格不存在则按 Step 0 模板补齐

### 产出类型 → 分区映射

| 产出类型 | 写入分区 | 路径示例 |
|----------|---------|---------|
| spec | `## 规划产出` | `specs/2026-05-20-foo-design.md` |
| plan | `## 规划产出` | `plans/2026-05-20-foo.md` |
| feature | `## 已完成功能` | `architecture/features/2026-05-20-foo.md` |
| pitfall | `## 已知坑点` | `architecture/pitfalls/2026-05-20-foo.md` |

### 追加格式

在对应表格最后一行数据行之后追加：

```
| 2026-05-20 | 主题描述 | specs/2026-05-20-foo.md |
```

---

## Step 4: Git 提交

### if is_git

```bash
git add docs/superpowers/
git commit -m "docs: 更新项目知识索引与架构文档（HANDOFF_PROTOCOL）"
```

> 警告：仅 `git add` 不 `git commit` 会导致知识固化结果在窗口关闭后丢失。

### else

跳过。

---

## Step 5: 退出宣告

向用户回复：

> 当前窗口的架构沉淀与防呆经验已安全落盘并提交。您现在可以执行 `/handoff` 命令进行状态交接。

---

## Step 6: 遗漏检测机制（供 /continue-handoff 使用）

判断上次窗口是否执行了本协议（不使用专用标记文件，通过 INDEX.md 与实际文件的差距判断）：

```
IF (specs/ 或 plans/ 存在 .md 文件)
  AND (INDEX.md「规划产出」表缺少这些文件条目)
THEN
  上次窗口的 HANDOFF_PROTOCOL 被跳过
  → /continue-handoff 触发回溯执行（补全 INDEX.md 索引）
```

如果缺失的是 feature/pitfall 文档本身（不只是索引条目），`/continue-handoff` 在初始化报告中标注 `(Missing Docs)` 提醒用户。

---

## 职责边界速查

| 组件 | 职责 | 触发时机 |
|------|------|---------|
| **本协议** | 确定性知识固化（features/pitfalls + INDEX.md + Git commit） | Plan 执行完毕、功能确认完成时 |
| **`/handoff`** | 动态状态交接（当前进度写入 plan 的 Handoff Context） | 窗口关闭前（需先完成本协议） |
| **`/continue-handoff`** | 新窗口预热（读取 INDEX.md + plan 恢复上下文） | 新窗口启动时 |
| **CLAUDE.md** | 入口规则（定义预热协议 + 交割纪律） | 始终生效 |
