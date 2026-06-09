# Preamble · 强制开始前流程

## 🚨 最高优先级硬约束 · 近 5 年卖方研报先行

> 做**行业分析**或**公司 / 个股分析**时，在任何定性分析输出之前，必须先阅读并提炼**近 5 年**相关卖方研究报告：
>
> - 首要来源：先通过 IMA MCP 搜索正文可稳定读取的固定知识库（ID 见 `core/adapters.md` 的“优先级 0”），包括智汇研券商投行研报精选、研万里 A 股调研纪要、研智声电话会议/路演纪要、研讯龙调研纪要点评；爱分享财经资讯仅作为补充线索源，不作为优先检索源。
> - 行业任务：先读该行业 / 主题近 5 年卖方行业报告、专题报告、策略报告的正文或 PDF 原文。
> - 公司 / 个股任务：先读该公司近 5 年公司报告，同时读其所属行业近 5 年行业报告。
> - 来源优先：IMA MCP 四个正文可读固定知识库搜索优先；之后东方财富 / dfcfw 的卖方报告正文、PDF 原文、转载正文优先；再调用妙想 skill 获取公告/财报、行情、财务、股东、事件、新闻、行业指标和定性研究材料；再接 `cn-web-search` 和 WebSearch；爱分享财经资讯只在优先来源不足时补充检索。
> - 使用方式：定性分析必须基于“IMA 知识库搜索 + 近 5 年卖方研报综合 + 妙想 skill 综合投研资料校验 + 后续 CN Web Search”展开，妙想 skill 获取的公司公告 / 财报等可追溯披露材料作为事实锚。
> - 禁止只看摘要：不能只汇总评级、目标价、PE、盈利预测、搜索摘要或 snippet；必须尽量读正文 / PDF。
> - 若找不到足够报告：必须在 Preflight / 内部缺口记录里标明；最终报告只在缺口影响核心结论时用短句说明，不单独输出“仍需补的资料”。

---

> 所有 sm-* skill 在产生任何分析输出**之前**，必须按本文件依序完成 6 个步骤。
> 这是治"幻觉"和"健忘"的核心机制——跳过任何一步视为未完成任务。
>
> v0.4 改动：新增 Step 0（任务断点检查），Steps 1-5 保留。

---

## Step 0 · 任务断点检查（v0.4 新增 · 治健忘）

在做任何其他事情之前：

1. **读 `.task-pulse`**（如果存在）
   - 不存在 → 视为新工作区，跳过本 step
   - 存在 → 解析 JSON，检查是否有进行中任务

2. **匹配本次请求**
   - 如果用户输入是"继续 t-XXX"或类似 → 直接进入 [checkpoint.md](checkpoint.md) 的恢复流程
   - 如果用户输入与 .task-pulse 中某个 in_progress 任务的 target 匹配 → 主动询问"你之前在做这个标的的 X 任务，要继续吗？"
   - 如果不匹配 → 创建新 task 条目，分配 task-id

3. **创建 task 条目**
   - 在 `.task-pulse` 添加新条目：`{id, skill, target, step:"0/N", ckpt:".checkpoint/{id}.md"}`
   - 创建空的 `.checkpoint/{id}.md` 文件

4. **Context budget 估算**
   - 如果当前会话已使用 > 150k tokens → 警告用户"建议本任务跑完后开新会话"
   - 如果 > 180k → 强制只完成当前段，写 checkpoint，停止

---

## Step 0.5 · 检查用户自定义模板和 skill（v0.7 新增 · 任务永久化）

在走标准路由之前，**必须**检查用户的 workspace 是否有自定义：

### 读取 user-templates/

```
检查 {workspace_root}/user-templates/*.md
读取每个文件的 frontmatter（name / trigger / based_on_skill）
把所有 trigger 收集成一个关键词表
```

### 读取 user-skills/

```
检查 {workspace_root}/user-skills/*/SKILL.md
读取每个 skill 的 frontmatter（name / extends / description / trigger）
```

### 匹配用户输入

按以下优先级：

1. **显式调用**：用户说"用 xxx 模板"或"用 my-xxx skill" → 精确匹配，直接加载
2. **自动路由**：用户输入包含某个 user-template 或 user-skill 的 `trigger:` 关键词 → 使用该定制
3. **命中多个**：列出候选让用户选
4. **零命中**：走默认 sm-* skill 路由

### 加载策略

**用户模板 (user-templates)**：
- 加载模板文件
- 加载 `based_on_skill` 指定的父 skill（作为执行框架）
- 输出时按模板的 `## 输出结构`，不用父 skill 默认结构
- 归档到模板的 `output_to:` 路径（覆盖 output-archive.md 的默认）

**L2 继承 skill (user-skills/ 带 extends:)**：
- 加载子 skill
- 加载 `extends:` 指定的父 skill
- 合并规则：子 skill 的新增段插入 / 追加到父 skill 的结构中
- 不能删除父 skill 的必需段

**L3 自创 skill (user-skills/ 不带 extends:)**：
- 直接加载该 SKILL.md
- 按它自己的结构和约束执行
- 仍然**强制**走 core/ 的 preamble / postamble / 后台事实可靠性自检 / 合规

### 不能被覆盖的规则

无论用户模板 / L2 / L3 怎么定制，以下规则**永远不能绕过**：

- ❌ `core/preamble.md` 6 步
- ❌ `core/postamble.md` 8 步
- ❌ 后台事实可靠性自检（常规高可信数据不逐条备注；弱来源、口径冲突或自行估算才短句说明）
- ❌ 关键缺口内部记录（不强制输出“仍需补的资料”段）
- ❌ 合规声明
- ❌ Dual Output Discipline

详见 [`user-templates.md`](user-templates.md) 和 [`user-skills.md`](user-skills.md)。

---

## Step 1 · 识别市场

按 [markets.md](markets.md) 确定标的的市场归属：

- `CN-A` — A 股 / 沪深
- `CN-FUND` — 公募基金
- `HK` — 港股
- `US` — 美股
- `GLOBAL` — 跨市场主题 / 行业

输出标记：`市场：{CN-A | CN-FUND | HK | US | GLOBAL}`

---

## Step 2 · 检查历史输出（治健忘）

按 [output-archive.md](output-archive.md) 的归档路径检查：

```
{coverage_root}/{ticker}/research/
{coverage_root}/{ticker}/{skill}/
```

**如果存在同标的、同 skill 的历史输出**：
- 读取最近一次输出
- 在本次输出开头声明：`本次为更新（上次：YYYY-MM-DD）`
- 重点输出"自上次以来的变化"，避免完全重写

**如果存在同标的、其他 skill 的历史输出**：
- 引用其结论作为本次工作的输入；若只是历史判断或自行推演，在相邻位置短句说明来源/口径
- 例：`命题来自 sm-thesis 输出 (2026-02-15)`

**如果完全无历史**：
- 在本次输出开头声明：`本次为首次研究`
- 进入下一步

---

## Step 3 · 检查任务进度（治健忘）

读取 `{workspace_root}/active-tasks.md`：

- 是否存在与本次任务相关的"进行中"任务？
- 如果是 → 读取 `progress` 字段，从断点继续
- 如果否 → 在本次工作开始时创建一条新的 active task

任务状态记录格式见 [`../setup/workspace/active-tasks.md.template`](../setup/workspace/active-tasks.md.template)。

---

## Step 4 · 输出 [Preflight] 取数计划（治幻觉）

按 [adapters.md](adapters.md) 的数据源决策树，**强制**输出以下结构：

```
[Preflight]
标的：{公司/行业/主题}
市场：{Step 1 的结果}
历史状态：{Step 2 的结果，"首次研究" 或 "更新（上次 YYYY-MM-DD）"}
任务进度：{Step 3 的结果，"新任务" 或 "续 task-id"}

数据源优先级链：
  1. {工具 A} → {预期拉取什么}
  2. {工具 B} → {备用 / 补充}
  3. {工具 C} → {兜底}

预期缺失项：
  - {可能拿不到的关键数据 1}
  - {可能拿不到的关键数据 2}
  → 这些只做内部记录；若影响核心结论，再在最终报告中短句说明
```

**⛔ 严禁跳过 Preflight 直接开始分析输出。**

如果用户没给标的代码或者市场不明确：
- 先问一句歧义澄清问题（仅限同名标的、市场不明这两种情况）
- 拿到答案后再走完 Preflight

---

## Step 5 · 按优先级实际取数

按 Preflight 写的优先级链，**实际调用工具拿数据**：

- **不要**只在 Preflight 里"声称"要拿什么，要真去拿
- 拿到的每条数据**立即**做后台可靠性判断（见 [evidence.md](evidence.md)）；常规高可信数据不逐条备注，弱来源、口径冲突或自行估算才在最终报告相邻位置短句说明
- 拿不到的数据**立即**记录到"缺失项实际清单"；只有影响核心结论时，才在最终报告中短句说明

---

## 完成 Preamble 之后

进入对应 skill 的具体分析流程。

分析输出的结尾必须按 [postamble.md](postamble.md) 走强制结束流程。

---

## 例外说明

**仅以下情况允许跳过 Preamble**：

- 用户明确说"不需要取数，我直接贴材料"——此时 Step 4 的优先级链直接写"用户提供材料"
- 用户明确说"快速看一下，不用深度"——此时仍需 Step 1/2/3，但 Step 4 可以简化

**任何其他情况跳过 Preamble 都视为违规。**
