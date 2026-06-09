# CLAUDE.md 注入模板

> 这是 setup.sh / update.sh 写入用户 `~/.claude/CLAUDE.md`（或 workspace CLAUDE.md）的标准内容。
> **带 begin/end marker**，支持幂等更新——下次 update.sh 只替换 marker 之间的内容，不影响用户其他 CLAUDE.md 内容。

---

## 注入的内容（复制到用户 CLAUDE.md 的部分，从 marker 开始）

```markdown
<!-- INVESTOR_HARNESS:BEGIN v0.6.0 -->
<!-- DO NOT EDIT MANUALLY — managed by investor-harness update.sh -->

# Investor Harness · 投研工作纪律（自动注入，勿改）

**version**: v0.6.0
**last_updated**: {{DATE}}
**harness_path**: {{HARNESS_PATH}}
**workspace_root**: {{WORKSPACE_ROOT}}
**data_sources**: {{DATA_SOURCES}}

## 启动协议（每次新会话第一件事）

1. 读 `{{HARNESS_PATH}}/core/_boot.md`（~1.2k tokens）
2. 检查当前目录的 `.task-pulse` 文件
3. 如有 in_progress 任务 → 主动告知用户："你有 N 个进行中任务，要继续哪一个？"
4. **不要默认从头开始，先问**

## 自动路由规则

我做投研任务时（股票、基金、行业、公司、财报、宏观、投资决策），你必须按 Investor Harness 纪律工作。**这是硬约束，不是建议**。

| 我说什么 | 你做什么 |
|---|---|
| "看一下 X" / "X 怎么样" | 走 `sm-autopilot` 自动路由 |
| "分析 X 公司" / "研究 X" / "看下 X" / "深度看 X" / "起 coverage" | 走 `ZZG` |
| "A 和 B 对比" / "A vs B" / "谁更好" / "相对估值" | 走 `ZZG2` |
| "X 财报前瞻" | 走 `sm-earnings-preview` |
| "反过来想 X" / "X 空头逻辑" | 走 `sm-red-team` |
| "X 预期差" | 走 `sm-consensus-watch` |
| "整理今天的 X" / "晨会" | 走 `sm-briefing` |
| "给 PM 一页纸" | 走 `sm-pm-brief` |
| "X 行业框架" / "X 产业链" | 走 `sm-industry-map` |
| "怎么问 X 管理层" | 走 `sm-roadshow-questions` |
| "看 X 的 K 线" / "复盘 X" | 走 `sm-tape-review` |
| "做 X 的 PPT" / "生成 deck" / "IC pitch" / "路演材料" | 走 `sm-deck-builder` |
| "刷新覆盖池" | 走 `sm-batch-refresh` |
| "扫事件" | 走 `sm-catalyst-sweep` |

## Skill 调用的强制流程

### 开始前 · Preamble 6 步
读 `{{HARNESS_PATH}}/core/preamble.md`，简化：
0. 检查 .task-pulse 续跑
1. 识别市场
2. 检查历史输出
3. 检查 active-tasks
4. **必须**输出 `[Preflight]` 取数计划
5. 实际取数

### 输出时
- 按 skill 结构
- 关键事实必须经过后台可靠性自检；最终正文不做标签化来源分级，不输出来源链或资料缺口大章；弱来源、口径冲突或自行估算才短句备注
- 风险必须可观测可触发（不要"宏观波动"套话）

### 结束后 · Postamble 8 步
读 `{{HARNESS_PATH}}/core/postamble.md`，简化：
0. 每完成一段写 .checkpoint
1. 后台事实可靠性自检
2. 内部记录资料缺口；最终报告只写影响核心结论的缺口
3. 合规声明
4. 归档输出到 `{{COVERAGE_ROOT}}/{ticker}/{skill}/YYYY-MM-DD-{skill}.md`
5. 更新 .task-pulse + active-tasks.md
6. 验收清单
7. **Dual Output Discipline** — 对话**贴完整输出** + 同时写文件；末尾追加 `📁 已归档:{path}` + 关键统计 + 下一步建议

⛔ **不要只回摘要**——云端用户打不开本地文件。默认必须对话 + 文件双输出。

## 数据源优先级

本机配置的数据源（按向导选择）：

{{DATA_SOURCES_PRIORITY_CHAIN}}

按上面的优先级链自动降级。缺失数据时走兜底协议让用户贴材料。

## 20 个基础 skill

`sm-master` · `sm-autopilot` · `sm-thesis` · `sm-industry-map` · `ZZG` · `sm-company-deepdive`（仅显式调用） · `ZZG2` · `sm-earnings-preview` · `sm-model-check` · `sm-consensus-watch` · `sm-industry-database` · `sm-catalyst-monitor` · `sm-roadshow-questions` · `sm-red-team` · `sm-pm-brief` · `sm-briefing` · `sm-tape-review` · `sm-deck-builder` · `sm-batch-refresh` · `sm-batch-earnings` · `sm-catalyst-sweep`

## 硬约束（违反等于未完成任务）

- ❌ 不要凭空编造数字
- ❌ 不要混淆事实和猜测
- ❌ 不要写套话风险
- ❌ 不要给目标价/评级（必须标注"需人工复核"）
- ❌ 不要承诺收益
- ❌ 不要只贴文件路径不贴内容
- ❌ 不要跳过 Preflight
- ❌ 不要把后台来源/口径备注、来源链或资料缺口清单写进正文

## Context Overflow 保护

- 剩余 > 30k → 正常运行
- 剩余 < 30k → 提醒"建议本任务跑完后开新会话"
- 剩余 < 10k → 强制写 checkpoint 后停止

## 默认行为

- 对模糊请求（"看看 X"）默认走 sm-autopilot
- 不主动追问背景
- 信息不足时列出"不知道什么"而不是猜

<!-- INVESTOR_HARNESS:END -->
```

---

## 占位符说明（setup.sh / update.sh 替换时用）

| 占位符 | 替换成 | 示例 |
|---|---|---|
| `{{DATE}}` | 当前日期 | `2026-04-07` |
| `{{HARNESS_PATH}}` | harness 安装路径 | `~/.claude/skills/investor-harness` 或 `~/investor-harness` |
| `{{WORKSPACE_ROOT}}` | 用户工作区路径 | `~/investor-research` 或 `~/投研` |
| `{{COVERAGE_ROOT}}` | 覆盖库路径（通常是 `{WORKSPACE_ROOT}/coverage`） | `~/investor-research/coverage` |
| `{{DATA_SOURCES}}` | 逗号分隔的数据源列表 | `miaoxiang,cn-web-search,websearch` |
| `{{DATA_SOURCES_PRIORITY_CHAIN}}` | 多行的优先级链描述 | 见下方 |

### `{{DATA_SOURCES_PRIORITY_CHAIN}}` 示例

用户选了妙想 skill + websearch：

```markdown
**A 股 / 公募**:
  1. IMA MCP 四个正文可读固定知识库（智汇研/研万里/研智声/研讯龙，ID 见 core/adapters.md；爱分享仅作补充线索）
  2. 妙想 skill A 股/公募（公告、财报、行情、财务、股东、事件、新闻、行业指标、定性研究材料）
  3. WebSearch（兜底）
  4. 用户手动贴材料

**港股**:
  1. IMA MCP 四个正文可读固定知识库（智汇研/研万里/研智声/研讯龙，ID 见 core/adapters.md；爱分享仅作补充线索）
  2. 东方财富近 5 年卖方研报正文/PDF/转载正文
  3. 妙想 skill 港股（公告、财报、行情、财务、事件、新闻、行业指标、定性研究材料）
  4. cn-web-search skill
  5. WebSearch
  6. 用户贴材料

**美股**:
  1. IMA MCP 四个正文可读固定知识库（智汇研/研万里/研智声/研讯龙，ID 见 core/adapters.md；爱分享仅作补充线索）
  2. 东方财富近 5 年卖方研报正文/PDF/转载正文
  3. 妙想 skill 美股（公告、财报、行情、财务、事件、新闻、行业指标、定性研究材料）
  4. WebSearch site:sec.gov
  5. WebFetch sec.gov
  6. 用户贴材料
```

用户选了妙想 skill + Alpha派 + 进门财经 + Wind + websearch：

```markdown
**A 股 / 公募**:
  1. IMA MCP 四个正文可读固定知识库（智汇研/研万里/研智声/研讯龙，ID 见 core/adapters.md；爱分享仅作补充线索）
  2. 妙想 skill（优先 A 股基础数据）
  3. Alpha派 MCP (补充 / 互验)
  4. Wind MCP (高质量财务数据)
  5. 进门财经 MCP (路演 / 专家 / 研报)
  6. WebSearch（兜底）

**港股 / 美股 / 其他**:
  1. IMA MCP 四个正文可读固定知识库（智汇研/研万里/研智声/研讯龙，ID 见 core/adapters.md；爱分享仅作补充线索）
  2. 东方财富近 5 年卖方研报正文/PDF/转载正文（港股 / 美股）
  3. 妙想 skill 港股 / 美股
  4. Wind MCP (全球覆盖，如已配置)
  5. WebSearch (SEC / HKEX)
  6. 用户贴材料
```

---

## 更新机制（marker 说明）

### 首次安装

setup.sh 追加整段（带 marker）到用户 CLAUDE.md 末尾。

### 后续更新

update.sh：
1. 读取用户 CLAUDE.md
2. 查找 `<!-- INVESTOR_HARNESS:BEGIN` 和 `<!-- INVESTOR_HARNESS:END -->`
3. 如果找到 → 替换中间内容为最新版本
4. 如果没找到 → 追加新段（用户可能之前手动删了 marker）
5. 替换前备份原文件到 `CLAUDE.md.backup-{timestamp}`

### Marker 格式的好处

- 用户可以在 marker 之外自由添加自己的 CLAUDE.md 内容
- 更新只影响 marker 之间的内容
- 用户明确知道哪段是自动管理的（"DO NOT EDIT MANUALLY"）
