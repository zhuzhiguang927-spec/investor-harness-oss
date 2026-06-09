---
name: ZZG2
description: >
  Investor Harness 公司对比分析默认入口。凡是用户要求“对比/比较/横向比较/同业对比/可比公司分析/相对估值/谁更好/哪个更值得看/哪个更优”，或使用
  “A vs B / compare X and Y / X 和 Y 对比”等表达，只要涉及两家或多家上市公司、股票或可识别公司实体，必须使用本 skill。
  不要用自由回答，不要退回 sm-company-deepdive 两次合并；先运行 ZZG2，再做公司对比研究。适用于 A 股、港股、美股和跨市场公司对比。
inputs:
  - 两家或多家上市公司名称 / 股票代码 / ticker
  - 可选：用户指定对比维度、持仓背景、关注周期、已有材料
outputs:
  - 完整公司对比分析报告 + 本地 Comparison Analysis 目录文件 + IMA Comparison Analysis note_id
data_sources: 以 Investor Harness 当前 AGENTS / core/adapters.md / core/markets.md 的最高优先级规则为准
markets: [CN-A, HK, US, GLOBAL]
official: false
---

# ZZG2 公司对比分析 Skill

## 最高优先级

用户让你“对比几家公司”时，本 skill 是默认入口。不要只做口头比较，也不要只分别跑多份公司深度再简单拼接；ZZG2 的任务是把多家公司放在同一口径下，回答“为什么这家公司，而不是另一家公司”。

本 skill 不限定只能对比两家公司。输入可以是两家公司，也可以是三家、五家或一组可识别上市公司。若用户给的是主题下的一组公司，先识别公司池和可比边界，再做同口径横向比较。

用户后续会继续定义具体分析方法。在用户补充前，先执行本文件的取数纪律、信息源顺序、归档和上传闸门；分析结构使用下方临时框架，后续可直接改本文件细化。

## 触发规则

看到以下任一意图，必须触发 ZZG2：

- `A 和 B 对比` / `比较 A 和 B` / `A vs B` / `compare A and B`
- `对比下这些公司` / `这几家公司谁更好` / `哪个更值得看` / `哪个更优`
- `同业对比` / `可比公司分析` / `横向比较` / `经营和估值比较`
- `相对估值` / `谁更便宜` / `谁的确定性更强` / `谁弹性更大`
- `A、B、C 怎么选` / `这几个标的放一起看`

不触发 ZZG2 的情况：

- 单家公司深度研究：走 `ZZG`
- 行业 / 赛道 / 产业链研究：走 `ZZG1`
- 从主题里筛候选标的：走 `sm-stock-screen` 或 `ZZG3`
- 盘中异动或纯交易监控：走 `sm-hourly-watch` / `sm-close-recap`

## 必读文件

执行前读取以下文件，采用其中更严格的约束：

- `{HARNESS_ROOT}\core\preamble.md`
- `{HARNESS_ROOT}\core\adapters.md`
- `{HARNESS_ROOT}\core\markets.md`
- `{HARNESS_ROOT}\core\postamble.md`
- `{HARNESS_ROOT}\core\output-archive.md`
- `{HARNESS_ROOT}\core\acceptance.md`
- `{HARNESS_ROOT}\skills\ZZG\SKILL.md`

## 输出位置与 IMA 上传完成闸门

公司对比分析必须输出到两个正式位置：

- IMA 笔记本：`Comparison Analysis`
- IMA folder_id：`{IMA_COMPARISON_ANALYSIS_FOLDER_ID}`
- 本地正式输出目录：`{OUTPUT_ROOT}\Comparison Analysis`

只有在完整 Markdown 成功上传到 IMA 笔记本 `Comparison Analysis`，且上传成功已被确认后，任务才算完成。若上传接口返回 `note_id`，只作为内部确认信号，不在最终回复展示，除非用户明确要求。

上传脚本参考 `ZZG` skill：

- 上传脚本：`{HARNESS_ROOT}\skills\ZZG\upload_to_ima.cjs`
- 标准命令：`node {HARNESS_ROOT}\skills\ZZG\upload_to_ima.cjs --file "{report_path}" --notebook "Comparison Analysis"`

文件命名规则：

- 两家公司：`{OUTPUT_ROOT}\Comparison Analysis\{公司A}_vs_{公司B}_公司对比分析报告.md`
- 多家公司：`{OUTPUT_ROOT}\Comparison Analysis\{比较主题或公司列表}_multi_company_公司对比分析报告.md`

没有写入本地正式输出目录、上传失败、无法确认上传成功、只在聊天里回复，都视为任务未完成。上传失败时，必须明确说明失败原因，不得把任务说成完成。

## 信息源纪律

在任何定性判断前，必须先完成资料读取和结构化校验。

### 1. 标的识别

逐家公司确认：

- 公司全称、简称、股票代码、交易所、市场标签
- 主营业务、所属行业、核心产品和主要下游
- 是否真的可比；若不可比，说明比较边界，而不是强行拉表

### 2. 结构化数据

逐家公司取数：

- 优先复用 `{HARNESS_ROOT}\skills\ZZG\data_agent.py` 获取市场和财务数据。
- 然后按 Investor Harness 当前规则调用同花顺 iFind MCP / 妙想等已配置结构化数据能力，校验公告、财报、行情、财务、股东、事件、新闻和行业指标。
- 港股和美股使用对应的 global_stock / 全球股票结构化数据工具。
- 跨市场比较必须注明会计准则、币种、报告期和披露频率差异。

### 3. 近 5 年卖方研报先行

逐家公司和共同所属行业读取过去 5 年卖方 / 券商研究报告正文或 PDF：

- 公司研报：公司深度、首次覆盖、年报点评、季报点评、跟踪报告。
- 行业研报：行业深度、产业链专题、供需格局、技术路线、竞争格局、政策和风险。
- 优先东方财富 / dfcfw 报告正文、PDF 原文、转载正文。
- 不得只看摘要、评级、目标价、PE 表或盈利预测摘要。

如果找不到足够正文 / PDF，或只能拿到摘要，必须在内部缺口记录中列明；最终报告只在该缺口影响核心结论时简短说明。

### 4. 补充搜索

完成上述步骤后，再使用：

- `cn-web-search`
- broader WebSearch
- 公司官网 / IR / 交易所 / SEC / 港交所等官方披露
- 用户贴的材料

补充搜索只用于补齐事实、口径和最近变化，不能替代研报正文和结构化数据。

## 临时分析框架

后续用户会继续定义细节；在此之前，完整报告先用以下结构：

1. `结论先行：核心差异和适用场景`
2. `标的识别与可比性边界`
3. `业务模式与产业链位置对比`
4. `收入结构与增长驱动对比`
5. `利润率、费用率与经营质量对比`
6. `资产负债表、现金流与资本开支对比`
7. `竞争壁垒、客户结构、技术路线与供给格局对比`
8. `估值、市场预期与预期差对比`
9. `催化剂、风险和验证节点`
10. `综合判断：谁更适合什么风险收益画像`

报告中必须有横向表格，至少覆盖：

- 市值、收入、归母净利润、收入增速、利润增速
- 毛利率、净利率、ROE / ROIC、经营现金流
- 研发费用率、销售费用率、管理费用率
- 主要业务占比、核心客户 / 下游、行业地位
- Forward PE / PB / PS / EV/EBITDA 等适合该行业的估值口径
- 未来 3-6 个月最重要的验证指标

## 证据表达

按当前 AGENTS 的硬约束，输出关键事实时带证据等级：

- `公开事实`
- `财报披露`
- `市场共识`
- `合理推演`
- `待核验假设`

写法要简洁，可以放在表格单元格或句尾括号中。不要把来源链、工具流程或资料检索过程写成长篇章节。

## 归档

正式归档建议写入比较任务目录：

`{workspace_root}/coverage/_comparisons/{YYYY-MM-DD}-{company-a}-vs-{company-b}-ZZG2.md`

如果比较对象超过两家公司：

`{workspace_root}/coverage/_comparisons/{YYYY-MM-DD}-{theme-or-first-company}-multi-company-ZZG2.md`

同时写入本地正式输出目录：

`{OUTPUT_ROOT}\Comparison Analysis\{比较主题或公司列表}_公司对比分析报告.md`

完成后必须上传 IMA，并在最终回复中给出：

- 本地正式报告路径
- 工作区归档路径
- IMA `note_id`

## 验收清单

完成前逐条自检：

- 已识别每家公司代码、市场、交易所和可比性边界。
- 已按每家公司读取近 5 年公司研报，并读取共同或相关行业研报。
- 已调用结构化数据工具校验公告、财报、行情、财务、股东、事件、新闻和行业指标。
- 已跑 `data_agent.py` 或明确说明为什么无法跑。
- 核心比较表口径一致；跨市场比较已处理币种、会计准则和报告期差异。
- 每个关键结论至少由财报披露、公告、结构化数据、研报正文或可追溯公开材料之一支撑。
- 输出不是多篇单公司报告拼接，而是同一口径下的横向比较。
- 已写入工作区归档文件和本地正式输出文件。
- 已上传 IMA `Comparison Analysis`，且上传成功已被确认。
- 若上传失败或无法确认上传成功，最终回复明确标记未完成。

## 合规

不构成买卖建议。涉及“谁更好”“是否更值得买”时，改写为“在什么前提、周期和风险收益画像下更占优”，不直接给无条件买卖指令。
