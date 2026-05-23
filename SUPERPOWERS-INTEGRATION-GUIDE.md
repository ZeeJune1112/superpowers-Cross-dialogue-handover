# Superpowers Skill 融合指南

本文档记录了从 Matt Pocock's skills 仓库借鉴并融合到 superpowers 的技能，以及完整的开发工作流设计。在新设备或 superpowers 更新后，按此文档重新配置即可恢复相同环境。

---

## 目录

1. [技能清单](#技能清单)
2. [部署步骤](#部署步骤)
3. [CLAUDE.md 修改](#claudemd-修改)
4. [完整开发流程](#完整开发流程)
5. [技能间关系说明](#技能间关系说明)
6. [CONTEXT.md 与 ADR 约定](#contextmd-与-adr-约定)
7. [常见问题](#常见问题)

---

## 技能清单

| 技能 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `caveman` | 新建 | Matt Pocock 改编 | Token 压缩通信模式 |
| `grill-me` | 新建 | Matt Pocock 改编 | 纯逻辑方案拷问 |
| `grill-with-docs` | 新建 | Matt Pocock 改编 | 领域模型驱动的方案拷问 |
| `systematic-debugging` | 修改 | diagnose 融合到 superpowers 原版 | 增强版 5 阶段调试 |

---

## 部署步骤

### 步骤 1：创建 caveman 技能

**路径**：`~/.claude/skills/caveman/SKILL.md`

```markdown
---
name: caveman
description: Ultra-compressed communication mode that cuts token usage ~75%. Use when the conversation is getting long, you want to save tokens, or user says "caveman mode", "be concise", "save tokens".
---

# Caveman Mode

An ultra-compressed communication mode. Drops filler, articles, and pleasantries. Fragments OK. Short synonyms preferred.

## Persistence

Once triggered, active in every response until the user explicitly says one of:
- `stop caveman`
- `normal mode`
- `exit caveman`

## Rules

- Drop articles (`a`, `an`, `the`)
- Drop filler words (`just`, `actually`, `really`, `well`)
- Drop pleasantries (`sure`, `happy to help`, `let me know`)
- Fragments OK — no need for full sentences
- Use short synonyms (`fix` over `resolve the issue`)
- Pattern: `[thing] [action] [reason]. [next step].`

## Examples

Normal: "I found the bug — it's in the auth middleware where the token refresh isn't being called on 401 responses. I'll fix it now."
Caveman: "Bug in auth middleware — no token refresh on 401. Fixing."

Normal: "Let me read the file first to understand the structure, then I'll make the change you requested."
Caveman: "Reading file. Then edit."

## Auto-Clarity Exception

Temporarily exit caveman mode for:
- Security warnings (vulnerabilities, secrets exposure)
- Irreversible actions (destructive ops, data loss risks)
- Critical ambiguity where compressed mode could cause misunderstanding

Resume caveman after the critical message: "Caveman resume. [continue]."
```

---

### 步骤 2：创建 grill-me 技能

**路径**：`~/.claude/skills/grill-me/SKILL.md`

```markdown
---
name: grill-me
description: Pure logic interview — challenges a plan through reasoning, edge cases, and architectural principles. Use when user says "grill me", "challenge my plan", "poke holes in this", or wants to stress-test a design through logic alone. Can be used standalone or inside brainstorming's design presentation phase. Do NOT use when user says "grill me WITH DOCS", mentions CONTEXT.md, domain glossary, or wants to challenge against documented domain language — those are grill-with-docs.
---

# Grill Me

Interview me relentlessly about every aspect of this plan or design until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one by one.

## How It Works

1. Ask questions **one at a time** — don't batch them
2. For each question, **provide your recommended answer** along with the reasoning
3. Explore the codebase instead of asking when a question can be answered by reading code
4. Keep drilling until every branch of the decision tree is resolved

## Question Areas

Cover these dimensions systematically:

- **Architecture** — module boundaries, interfaces, data flow
- **Data** — schema, state management, caching, persistence
- **Edge cases** — error states, empty states, concurrency, race conditions
- **Security** — auth, authorization, input validation, secrets
- **Performance** — bottlenecks, N+1 queries, unnecessary work
- **Testing** — what to test, how to test, what's hard to test
- **Deployment** — migrations, rollback, feature flags, backwards compatibility
- **Dependencies** — external services, API contracts, failure modes

## Rules

- Don't accept vague answers — ask for concrete scenarios
- If two decisions depend on each other, resolve one first, then revisit the other
- When the user contradicts themselves, point it out
- If the plan has a gap, say so directly and propose how to fill it
- Stop when the user says "that's enough" or all branches are resolved

## Compatibility with brainstorming

When the `superpowers:brainstorming` skill is active, grill-me operates **inside** the design presentation phase — not after brainstorming completes. This avoids conflicting with brainstorming's hard terminal state (writing-plans).

How to use grill-me within brainstorming:
- When the agent presents a design section and asks "does this look right?", respond with "grill me on this section" to trigger the challenge loop
- When the full design is presented but the spec hasn't been written yet, say "before you write the spec, grill me on this design"
- Grill until satisfied, then let brainstorming resume its normal flow (write spec → user review → writing-plans)

When used standalone (no brainstorming active), grill-me is a self-contained challenge interview with no downstream file output.

## Example Flow

```
Agent: First — what's the trigger for this feature? Is it user-initiated, scheduled, or event-driven?
User: User clicks "export" on the dashboard.

Agent: OK. Will the export be synchronous (user waits) or async (user gets notified when ready)?
User: Async, the data can be large.

Agent: That means you'll need a job queue and a notification mechanism.
  What happens if the export job fails midway — retry, or show a partial file?
...
```
```

---

### 步骤 3：创建 grill-with-docs 技能

**路径**：`~/.claude/skills/grill-with-docs/SKILL.md`

```markdown
---
name: grill-with-docs
description: Domain-aware grilling — challenges your plan against the project's domain glossary (CONTEXT.md), architecture decisions (ADRs), and actual codebase behavior. Sharpen terminology, catch contradictions, update CONTEXT.md inline. Use when user says "grill me with docs", "grill against the domain model", "challenge against CONTEXT.md", or explicitly wants documentation involved in the grilling. Do NOT use when user says "grill me" alone without mentioning docs/CONTEXT.md — that's grill-me.
---

# Grill With Docs

Interview me relentlessly about every aspect of this plan, challenging it against the project's domain glossary (`CONTEXT.md`) and architecture decision records (`docs/adr/`). Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

Ask questions **one at a time**, providing your recommended answer with reasoning. If a question can be answered by exploring the codebase, explore the codebase instead of asking.

## Bootstrap: CONTEXT.md

Before grilling, check whether `CONTEXT.md` exists at the project root.

**If it exists** — load it. Use it as the authoritative domain glossary for the entire session.

**If it doesn't exist** — do NOT start grilling. Instead:
1. Say: "There's no CONTEXT.md yet. This grilling session will be much stronger with one. I can create a stub from the codebase — it takes a few minutes and gives us a shared vocabulary to work from. Want me to?"
2. If user says yes: explore the codebase for domain terminology (model names, event names, business concepts, bounded contexts), write a draft `CONTEXT.md` at the project root, and ask the user to review it before proceeding to the grilling session.
3. If user says no: fall back to `grill-me` mode (pure logic interview without domain docs).

## CONTEXT.md Format

`CONTEXT.md` is a glossary and nothing else. It must be **totally devoid of implementation details** — no file paths, no class names, no code structure. It describes the business domain in the project's own language.

```markdown
# Context

## <Domain Concept 1>

A one-paragraph definition using only domain language. What is it? Who uses it?
What does it represent in the real world? Avoid technical implementation details.

## <Domain Concept 2>

...
```

Example of good vs bad entries:

| Good (domain language) | Bad (implementation) |
|---|---|
| **Order**: A customer's request to purchase one or more products. An order is Pending until payment is confirmed, then becomes Confirmed. | **Order**: Stored in the `orders` table with a `status` enum. Handled by `OrderService.create()`. |

## ADR Format

Only offer to create an ADR when ALL three are true:
1. **Hard to reverse** — changing your mind later has meaningful cost
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any is missing, skip the ADR.

ADRs live in `docs/adr/`, numbered sequentially: `0001-<slug>.md`.

```markdown
# ADR 0001: <Title>

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXXX

**Context:** What is the problem? What constraints are we working under?

**Decision:** What did we decide? One or two sentences.

**Consequences:** What becomes easier? What becomes harder? What's the migration path?
```

## During the Session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately: "Your glossary defines 'Cancellation' as full-order cancellation, but you seem to mean partial line-item cancellation — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term: "You're saying 'account' — do you mean the Customer account or the Billing account? Those are different things in this domain."

### Discuss concrete scenarios

Invent scenarios that probe edge cases and force precision about the boundaries between concepts. Don't settle for abstract agreement.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update CONTEXT.md inline

When a term is resolved or a new concept crystallises, update `CONTEXT.md` right there. Don't batch — capture as they happen. Keep entries in the glossary format: domain language only, no implementation details.

## Compatibility with brainstorming

Same pattern as `grill-me`: operates **inside** brainstorming's design presentation phase, not after it completes.

- When the agent presents a design section, say "grill me with docs on this section" to trigger the domain-aware challenge loop
- When the full design is presented but the spec hasn't been written, say "before the spec, grill me with docs"
- Grill until satisfied, then let brainstorming resume normal flow (write spec → user review → writing-plans)

When used standalone (no brainstorming active), grill-with-docs is a self-contained domain-aware challenge interview.

## vs grill-me

| | grill-me | grill-with-docs |
|---|---|---|
| Challenges against | Pure logic, edge cases, architecture principles | Domain glossary, ADRs, codebase terminology |
| Requires CONTEXT.md | No | Yes (creates if missing) |
| Updates docs | No | Updates CONTEXT.md and creates ADRs inline |
| Use when | No domain docs exist, or quick gut-check | Domain language is established, want precision |

If CONTEXT.md is well-maintained, prefer grill-with-docs. If the project has no domain documentation yet, grill-with-docs will bootstrap it — giving you a glossary to carry forward.
```

---

### 步骤 4：增强 systematic-debugging

superpowers 更新后，`systematic-debugging` 会被覆盖回原版。需要重新融合 diagnose 的四个特性。

**文件路径**：`~/.claude/plugins/cache/claude-plugins-official/superpowers/<version>/skills/systematic-debugging/SKILL.md`

需要做以下 5 处修改：

#### 修改 1：标题 "The Four Phases" → "The Five Phases"

搜索 `## The Four Phases`，改为 `## The Five Phases`。

#### 修改 2：Phase 1 Step 2 — 扩展为反馈循环构建

搜索：
```
2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess
```

替换为：
```
2. **Reproduce Consistently — Build a Fast Feedback Loop**

   A 2-second deterministic loop is a debugging superpower; a flaky 30-second one is dead weight. Choose the fastest reliable strategy:

   Strategies in order of preference:
   1. **Unit test** — isolated, fastest, most repeatable
   2. **Integration test** — if the bug spans module boundaries
   3. **Reproduction script** — single-file script that triggers the bug
   4. **Minimal app** — stripped-down version of the app
   5. **Curl/httpie call** — for API bugs
   6. **Browser console snippet** — for frontend bugs
   7. **Dev server with hot reload** — for visual bugs
   8. **Log injection** — add targeted logging at suspected failure points
   9. **Debugger breakpoint** — last resort for complex state
   10. **HITL bash script** — absolute last resort, manual step-by-step

   - Can you trigger it reliably with the chosen strategy?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → identify what makes it flaky (timing, data, environment, concurrency), then gather more data, don't guess
```

#### 修改 3：Phase 1 Step 4 — 添加插桩标记规则

搜索 `**WHEN system has multiple components`，在它上方插入一行：

```
   **Tagging rule:** ALL debug output must use a unique prefix like `[DEBUG-a4f2]` so it can be removed in a single pass after the fix. Do not leave debug instrumentation in the code.
```

同时在该步骤的代码块末尾，`investigate that specific component` 之后添加：

```
   THEN clean up ALL debug output (search for [DEBUG-xxxx])
```

#### 修改 4：Phase 3 — 添加多假设排名

搜索：
```
### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague
```

替换为：
```
### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Hypotheses**

   **For straightforward bugs** (clear error, known pattern):
   - State clearly: "I think X is the root cause because Y"
   - Single hypothesis, be specific

   **For complex or unfamiliar bugs** (unclear root cause, multiple suspects, unfamiliar code):
   - Generate **3-5 ranked hypotheses** before testing any of them
   - Each hypothesis must be:
     - **Falsifiable** — provably wrong or right through instrumentation
     - **Specific** — names the line, method, or condition at fault
     - **Ranked** — ordered by likelihood based on evidence observed
   - Ranking forces you to think about what's most likely before diving in. The first idea that comes to mind is often wrong.
```

同时将 Step 3 "Verify Before Continuing" 中的：
```
   - Didn't work? Form NEW hypothesis
```
改为：
```
   - Didn't work? Move to next ranked hypothesis (if using multi-hypothesis) OR form new hypothesis
```

#### 修改 5：Phase 4 — 添加 Post-Mortem

在 Phase 4 中搜索 `4. **If Fix Doesn't Work**`，在该 block 之后、`5. **If 3+ Fixes Failed` 之前插入：

```
5. **Post-Mortem (hard bugs)**

   After a hard bug is fixed, record what was learned. This converts debugging pain into permanent knowledge:
   - **Root cause** in one sentence
   - **Why existing tests didn't catch it** — what test gap existed?
   - **What architectural change would prevent this class of bug** — don't expand scope of the fix, but note the improvement for future planning
   - **Cleanup** — strip ALL debug instrumentation (search for the `[DEBUG-xxxx]` prefix)
```

然后将原来的 `5. **If 3+ Fixes Failed: Question Architecture**` 重编号为 `6`。

#### 修改 6：更新 Quick Reference 表

搜索：
```
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |
```

替换为：
```
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass |
| **5. Post-Mortem** | Record root cause, identify test gap, suggest architectural fix, clean up debug output | Learning captured, instrumentation removed |
```

并在 Phase 1 的行中，`check changes, gather evidence` 改为 `reproduce (build fast feedback loop), check changes, gather tagged evidence`。

---

## CLAUDE.md 修改

在 `~/.claude/CLAUDE.md`（全局配置）末尾追加以下章节：

```markdown
## Project Domain Awareness

Before any domain-sensitive work (design, naming, schema changes, behavior modeling), if `CONTEXT.md` exists at the project root, read it first to understand the project's domain language. If `docs/adr/` exists, skim the most recent ADRs for relevant architectural constraints.

When writing code or docs, use the terms defined in `CONTEXT.md` — no synonyms, no vagueness. If a new term crystallizes, propose adding it to `CONTEXT.md` (use `/grill-with-docs` to refine it).
```

---

## 完整开发流程

```
                        项目初始化（每个新项目只做一次）
                        ─────────────────────────────
                        /grill-with-docs
                          ├─ 没有 CONTEXT.md → Agent 从代码库提取领域术语
                          │                     → 生成 CONTEXT.md（业务词典）
                          │                     → 拷打过程中创建 ADRs（架构决策）
                          └─ 已有 CONTEXT.md → 加载 + 拷打更新


                        日常开发流程
                        ────────────

                        有想法
                          │
                    ┌─────▼──────┐
                    │ brainstorming │  ← 自动触发（任何创意/功能/改动）
                    │               │  ← 读 CONTEXT.md + ADRs（CLAUDE.md 指令）
                    └─────┬──────┘
                          │
                    提问 + 探索项目
                          │
                    呈现设计（逐节确认）
                          │
                    ┌─────▼──────┐
                    │    拷打     │
                    │            │
                    │ 有 CONTEXT.md  ──→ /grill-with-docs
                    │            │      挑战：术语是否一致？代码是否吻合？
                    │            │      输出：更新 CONTEXT.md / 创建 ADR
                    │            │
                    │ 无 CONTEXT.md  ──→ /grill-me
                    │            │      挑战：逻辑漏洞？边界情况？架构缺陷？
                    │            │      输出：无文件，纯共享理解
                    │            │
                    │ 满意了说 "that's enough" ──→ 恢复 brainstorming
                    └─────┬──────┘
                          │
                    ┌─────▼──────┐
                    │ writing-plans │  ← 出 spec（docs/superpowers/specs/）
                    │               │  ← 出 plan（docs/superpowers/plans/）
                    └─────┬──────┘
                          │
                    ┌─────▼────────────────┐
                    │ subagent-driven-      │  ← 并行执行 plan 中的独立任务
                    │ development           │
                    └─────┬────────────────┘
                          │
                    ┌─────▼──────────┐
                    │ verification-   │  ← 硬门：跑验证命令，看输出
                    │ before-         │  ← 不允许 "我觉得修好了"
                    │ completion      │  ← ⚠️ 容易跳过，需要 CLAUDE.md 强制
                    └─────┬──────────┘
                          │
                    手动抽查验证
                          │
                    ┌─────▼──────┐
                    │systematic-  │  ← 遇到 bug → 五阶段调试：
                    │debugging    │      1. 根因（构建快速反馈循环）
                    │(已增强)     │      2. 模式（找对比例子）
                    │             │      3. 假设（简单 1 个 / 复杂 3-5 个排名）
                    │             │      4. 修复（最小改动 + 回归测试）
                    │             │      5. 复盘（记录教训，清理 [DEBUG-xxxx]）
                    │             │
                    │ ◄── 循环直到通过 ──┘
                    └─────┬──────┘
                          │
                    ┌─────▼──────┐ (可选，大改动时加)
                    │ requesting- │  ← 提交前代码审查
                    │ code-review │
                    └─────┬──────┘
                          │
                    ┌─────▼─────────┐
                    │ finishing-a-   │  ← 合并/PR/清理分支
                    │ development-   │
                    │ branch         │
                    └───────────────┘


                        随时可用
                        ────────

                        caveman mode  ← 长会话时节省 75% Token
                                         说 "caveman mode" 开启
                                         说 "normal mode" 退出
```

---

## 技能间关系说明

### 触发词互斥

| 你说 | 触发 |
|------|------|
| `grill me` | grill-me |
| `grill me with docs` | grill-with-docs |
| `challenge my plan` | grill-me |
| `challenge against CONTEXT.md` | grill-with-docs |
| `poke holes in this` | grill-me |

grill-me 和 grill-with-docs 的 frontmatter description 中各自包含互斥声明：
- grill-me 的 description 末尾：`Do NOT use when user says "grill me WITH DOCS", mentions CONTEXT.md, domain glossary...`
- grill-with-docs 的 description 末尾：`Do NOT use when user says "grill me" alone without mentioning docs/CONTEXT.md — that's grill-me.`

### 文件产出不冲突

| 技能 | 产出 | 位置 |
|------|------|------|
| grill-with-docs | 领域术语表 | `CONTEXT.md`（项目根） |
| grill-with-docs | 架构决策 | `docs/adr/000X-slug.md` |
| brainstorming | 设计 spec | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` |
| writing-plans | 实施计划 | `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` |
| systematic-debugging | 临时插桩 `[DEBUG-xxxx]` | 代码中（Phase 5 清理） |

四组路径互不重叠。superpowers 全线扫描中零处引用 `CONTEXT.md` 或 `docs/adr/`。

### 与 brainstorming 的兼容性

grill-me 和 grill-with-docs 均明确声明 **仅在 brainstorming 的"呈现设计"阶段内运行**，不越界。brainstorming 的 HARD GATE（禁止实现）和终端状态（writing-plans）不受影响。

---

## CONTEXT.md 与 ADR 约定

### CONTEXT.md

- **是什么**：业务领域词典，纯领域语言
- **不是什么**：spec、实现文档、代码映射
- **格式**：`## <概念名>` + 一段纯领域语言定义
- **禁止**：文件路径、类名、表名、代码结构

### ADR

- **创建条件（三条件全满足才写）**：
  1. 难逆转
  2. 无上下文时令人费解
  3. 真实权衡结果

- **位置**：`docs/adr/0001-<slug>.md`
- **格式**：Status / Context / Decision / Consequences

---

## 常见问题

### Q: superpowers 更新后怎么办？

1. 重新创建 `caveman`、`grill-me`、`grill-with-docs` 三个目录（插件更新不会删除 `~/.claude/skills/` 下的自定义技能，但以防万一）
2. 重新按步骤 4 修改 `systematic-debugging`（这个一定会被覆盖）
3. 检查 `~/.claude/CLAUDE.md` 中的 "Project Domain Awareness" 章节是否还在

### Q: 新项目第一次用 grill-with-docs 会怎样？

Agent 发现没有 `CONTEXT.md`，主动 offer 从代码库提取领域术语创建一份草稿。你审核通过后，grilling 开始。拷打中确定的术语自动写入 `CONTEXT.md`。

### Q: grill-me 和 grill-with-docs 怎么选？

- 项目有 `CONTEXT.md` → `/grill-with-docs`（领域模型驱动的拷打）
- 项目没有也不想建 → `/grill-me`（纯逻辑拷打）
- 不确定 → 先说 `/grill-me`，需要领域模型时再切

### Q: verification-before-completion 为什么容易跳过？

subagent-driven-development 的流程终点直接指向 finishing，中间没有强制 verification 门。建议在 CLAUDE.md 中加一条规则强制执行。
