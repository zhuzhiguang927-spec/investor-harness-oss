<!-- investor-harness:keyword-routes:start v0.9.2 -->
<!--
  这块由 investor-harness ONBOARDING.md 自动管理。
  下次升级时整块替换。**不要手动编辑**——改 setup/keyword-routes.md 然后重跑 onboarding。
  Source: https://github.com/joansongjr/investor-harness/blob/main/setup/keyword-routes.md
-->

## Investor Harness 关键词路由（自动注入）

当用户对话里出现以下关键词时，**LLM 必须按对应 skill 的规则工作**（按 core/_boot.md 三层加载）：

### 默认路由（24 个）

| 用户说 | 走 skill |
|---|---|
| 看看 X / X 怎么样 / 帮我看下 X | `sm-autopilot`（模糊路由） |
| master 模式 / 总控 / 全套跑一遍 X | `sm-master` |
| X 投资命题 / X 的 thesis / X 投资逻辑 | `sm-thesis` |
| X 行业框架 / X 产业链地图 / X 行业全景 | `ZZG1`（行业研究默认入口） |
| **分析 X 公司 / 研究 X / 看下 X / X 深度报告 / 深度看 X / 起 X 的 coverage** | `ZZG`（公司/个股研究强制默认入口；`sm-company-deepdive` 仅在显式点名时使用） |
| **A 和 B 对比 / 比较 A 和 B / A vs B / 谁更好 / 相对估值 / 同业对比 / 可比公司分析** | `ZZG2`（公司对比分析默认入口） |
| **事件驱动分析 / 事件驱动选股 / 这件事对 X 有啥影响 / 这件事对哪些公司利好 / 这个业绩怎么看 / 这段变化哪些公司受益 / 这段信息怎么选股 / 哪些公司值得投资 / 哪些票值得看** | `ZZG3`（事件/变化/业绩材料 → 公司影响判断与投资候选分层） |
| **X 财报前瞻 / X earnings preview / X 业绩前瞻** | `sm-earnings-preview` |
| 审 X 的模型 / X 模型 sanity check / X 模型审阅 | `sm-model-check` |
| **X 预期差 / X consensus / X 一致预期** | `sm-consensus-watch` |
| 数据库 / 产业数据库 / 公司数据库 / 数据底表 / 指标库 | `sm-industry-database` |
| X 催化剂 / X catalyst / X 事件跟踪 | `sm-catalyst-monitor`（若要从事件筛投资候选公司则走 `ZZG3`） |
| 怎么问 X 管理层 / X 调研提纲 / X 路演问题 | `sm-roadshow-questions` |
| 盯盘 / 看盘 / 每小时看一下 X / X 盘中异动 | `sm-hourly-watch` |
| 收盘后复盘 / 股票池复盘 / 今天为什么涨跌 / 盘后复盘 | `sm-close-recap` |
| **反过来想 X / X 空头逻辑 / X red team / X 反方** | `sm-red-team` |
| 选股 / 筛标的 / 挖标的 / AI 链里还缺什么 / 涨得少的 AI 板块 | `sm-stock-screen` |
| **给 PM 一页纸 / X 的 PM brief / IC 一页纸** | `sm-pm-brief` |
| 晨会 / 晚报 / 整理今天的 X / 路演摘要 | `sm-briefing` |
| 看 X 的 K 线 / 复盘 X / X 盘面 / X 技术面 | `sm-tape-review` |
| **做 X 的 deck / X 的 IC pitch PPT / X 路演 PPT / X 客户 pitch** | `sm-deck-builder` |
| 刷新覆盖池 / 批量过 X 列表 / coverage refresh | `sm-batch-refresh` |
| 财报季批量 / 批量前瞻 / batch earnings | `sm-batch-earnings` |
| 扫事件 / 今天有什么催化 / catalyst sweep | `sm-catalyst-sweep` |

### Librarian 模式（v0.9+ · opt-in · 6 个）

> 仅当用户明示以下关键词时启用，**不在 sm-autopilot 默认路由内**。

| 用户说 | 走 skill |
|---|---|
| **起 X 的 wiki page / 建 X 的 coverage / onboard X** | `sm-wiki-build` |
| **刷 daily feed / 跑每日扫描 / 今天看一下覆盖池** | `sm-daily-feed` |
| **见 X 前过一遍 question list / 准备 X 调研提纲 / 会前 briefing** | `sm-question-list` |
| **跑健康检查 / 扫跨源矛盾 / wiki 自检** | `sm-health-check` |
| **会后归档 / 整理 X 的 Q&A / 见完 X 后整理** | `sm-qa-archive` |
| **关键人物追踪 / 跟踪 X 博主 / 跟踪 Reddit / 人物 watch** | `sm-people-watch` |

### 硬约束（所有路由都强制）

1. 如果当前工作区缺少 `coverage/` / `themes/` / `briefings/` / `.task-pulse` / `active-tasks.md`，先提示用户补建；**只装路由不算 setup 完成**
2. A 股、港股和美股资料来源顺序：IMA MCP 四个正文可读固定知识库（知识库 ID 见 `core/adapters.md`，先搜智汇研、研万里、研智声、研讯龙；爱分享财经资讯仅作补充线索源，不作为优先检索源） → 东方财富近 5 年卖方研报定性材料（读正文/PDF/转载正文，重点是行业和公司分析；不默认汇总评级、盈利预测、PE） → 妙想 skill（公告/财报、行情、财务、股东、事件、新闻、行业指标和定性研究材料；A 股、港股、美股分别使用妙想对应市场能力） → `cn-web-search` → WebSearch → 用户贴材料；不使用 AIMI / agent_chat，不默认使用巨潮
3. 开始前：跑 [`core/preamble.md`](INVESTOR_HARNESS_PATH/core/preamble.md) 6 步；但公司/个股研究命中 `ZZG`、公司对比命中 `ZZG2`、行业研究命中 `ZZG1` 时，按对应 skill 自己的流程执行，不套 `sm-company-deepdive`
4. 输出时：后台做事实可靠性自检；最终正文不做标签化来源分级，不输出来源链或资料缺口大章；弱来源、口径冲突或自行估算才短句备注
5. 结束后：跑 [`core/postamble.md`](INVESTOR_HARNESS_PATH/core/postamble.md) 8 步
6. 覆盖池 / 单标的任务必须归档到 `{coverage_root}/{ticker}_{name}/...`，只留在对话里视为未完成
7. 双输出：对话贴完整内容 + 写入文件，末尾追加 📁 已归档提示
8. 凡命中 `ZZG` / `ZZG1` / `ZZG2` / `ZZG3` 或其他明确要求上传输出结果的 skill，必须把该 skill 产出的完整结果文件按其 `SKILL.md` 指定的本地正式输出位置、归档位置、IMA 笔记本和上传命令执行；harness 层不硬编码具体目录、folder_id 或笔记本名。最终回复只需要给出本地文件路径和 IMA 已上传确认，不输出 `note_id`，除非用户明确要求；本地写入失败、归档失败、上传失败、无法确认上传成功、只写本地文件或只贴对话，都视为未完成。

⛔ 不编数据 · 不当替代持牌分析师 · 不构成买卖建议

详细 skill 文档：`INVESTOR_HARNESS_PATH/skills/{skill-name}/SKILL.md`
完整路由表：`INVESTOR_HARNESS_PATH/setup/keyword-routes.md`

<!-- investor-harness:keyword-routes:end -->
