# Superpowers 跨窗口记忆固化协议

本协议是 CLAUDE.md 中「核心交割纪律」的具体实现，解决两个问题：
1. **固化**：当前窗口的确定性知识（规划产出、功能成果、踩坑经验）在关闭前落盘
2. **预热**：新窗口启动时（通过 `/continue-handoff` 触发）快速加载这些知识，避免重复踩坑

> **CLAUDE.md 中的规则指向本文件，本文件指向 INDEX.md。continue-handoff 技能在新窗口触发时读取 INDEX.md 完成预热。四层关系：**
> ```
> CLAUDE.md ──(指针)──→ HANDOFF_PROTOCOL.md  ← 交棒时执行（写入知识）
> CLAUDE.md ──(指针)──→ INDEX.md              ← 预热时读取（由 continue-handoff 技能自动执行）
> HANDOFF_PROTOCOL.md ──(更新)──→ INDEX.md     ← 本协议维护索引
> /continue-handoff ──(读取)──→ INDEX.md        ← 新窗口恢复入口
> ```

---

## 0. 环境检测与初始化

### 环境检测
执行协议前，先判断当前环境：

| 检测方式 | 命令 | 结果 |
|----------|------|------|
| Git 仓库 | `git rev-parse --is-inside-work-tree` | 输出 `true` → 走 Git 流程 |
| 非 Git | 命令失败或输出错误 | 走非 Git 流程 |

两种流程的区别仅在第 1 步（审查改动范围）和第 4 步（Git 提交），其余步骤完全相同。

### 首次使用初始化

以下条件按需创建，缺失任何一项都不阻塞流程——创建即可继续：

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

---

## 1. 审查改动范围

### Git 流程
1. `git diff --stat` — 查看本次窗口改动了哪些文件
2. `git diff` — 查看具体改动内容
3. 筛选：聚焦于生产代码变更、配置变更、依赖变更、文档产出（spec/plan/feature/pitfall）。忽略临时性内容（如 `console.log` 调试行、被后续 commit 覆盖的中间状态文件）

### 非 Git 流程
1. 回顾本次窗口对话，列出实际创建或修改的文件
2. 回顾本次窗口中遇到的错误、反复调试的环节
3. 筛选：同上，聚焦确定性知识，忽略临时调试代码

---

## 2. 事务性落盘

根据第 1 步的审查结果，判断需要写入哪些分类的详细文档：

### 写入 `docs/superpowers/architecture/features/`（功能归档）
- **触发条件**：实现了新功能或重构了公共模块，且已通过测试验证
- **文件命名**：`YYYY-MM-DD-<主题>.md`
- **内容要求**：功能概述、关键设计决策、核心文件路径

### 写入 `docs/superpowers/architecture/pitfalls/`（坑点归档）
- **触发条件**：攻克了隐蔽 Bug、配置暗坑、环境问题
- **文件命名**：`YYYY-MM-DD-<主题>.md`
- **内容要求**：问题现象、根因分析、确定性规避手段

### 无额外落盘内容时
如果本次窗口未产生 features 或 pitfalls，跳过本步骤，直接进入第 3 步。不要为了"完成步骤"而写入低价值内容。

> **注意**：spec 和 plan 文件由 superpowers 流程（brainstorming → writing-plans）自动生成到 `specs/` 和 `plans/` 目录，不属于本步骤的落盘范围。本步骤只负责 features 和 pitfalls。

---

## 3. 更新索引（必选步骤，不可跳过）

将本次窗口的所有产出追加到 **`docs/superpowers/architecture/INDEX.md`** 的对应表格中。

### 追加规则
- 在 INDEX.md 对应分区表格的末尾追加新行
- 路径使用相对于 `docs/superpowers/` 的路径
- 追加前先检查：如果已有相同「日期 + 主题」的行，跳过不重复添加
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
git commit -m "docs: 更新项目知识索引与架构文档"
```

非 Git 环境跳过此步。

**重要**：仅 `git add` 而不 `git commit` 会导致知识固化结果在窗口关闭后丢失。必须完成 commit。

---

## 5. 退出宣告

完成上述步骤后，向用户回复：

> 当前窗口的架构沉淀与防呆经验已安全落盘并提交。您现在可以执行 `/handoff` 命令进行状态交接。

**注意**：`/handoff` 是 superpowers 提供的用户命令，负责将当前任务的动态状态（进行到哪一步、待办队列）写入 plan 文件。本协议负责在此之前完成确定性知识（features、pitfalls、INDEX.md）的固化落盘。两者各司其职、缺一不可。

---

## 6. 遗漏检测机制（供 continue-handoff 使用）

本协议是否已执行，不会在文件系统中写入专用标记文件。continue-handoff 技能通过以下方式检测上次是否遗漏了 HANDOFF_PROTOCOL：

```
检测方法: 对比 INDEX.md 索引 vs 目录实际文件

specs/ 或 plans/ 目录存在 .md 文件
  AND
INDEX.md「规划产出」表中缺少这些文件的条目
  →
上次窗口的 HANDOFF_PROTOCOL 被跳过
  →
continue-handoff 回溯执行本协议（至少补全 INDEX.md 索引）
```

**为什么不用专用标记文件**：标记文件会引入状态不一致风险（标记存在但索引过期）。以 INDEX.md 与实际文件的差距作为信号，本身就是最真实的完成状态。无需额外标记。

---

## 附：新窗口预热流程

新窗口触发 `/continue-handoff` 后，continue-handoff 技能和 CLAUDE.md 预热协议共同完成以下流程：

```
/continue-handoff 触发
  ↓
continue-handoff 技能第 0 步：读取 INDEX.md
  ↓ INDEX.md 存在
按索引表格逐条读取 specs/  plans/  features/  pitfalls/
  ↓ INDEX.md 缺失/空
扫描并逐个读取四个目录中的所有 .md 文件
  ↓ 目录也为空
跳过预热，依赖 handoff 上下文继续
  ↓
continue-handoff 技能第 1 步：挂载 Plan 文件并提取 Handoff Context
  ↓
拥有项目全貌 + 当前任务状态，开始工作
```

### 为什么不会卡死
- INDEX.md 不存在 → 兜底到目录扫描 + 逐个读取
- 目录也不存在 → 跳过预热，Plan 文件和 Handoff Context 仍然可达
- CLAUDE.md 始终被加载 → 指针始终可达
- HANDOFF_PROTOCOL.md 第 0 步的初始化确保下次不再缺失基础设施
