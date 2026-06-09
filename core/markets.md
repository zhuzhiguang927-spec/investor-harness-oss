# Markets

Investor Harness 覆盖的市场范围与识别规则。

## 支持的市场

| 标签 | 市场 | 识别特征 | 主要数据源 |
|---|---|---|---|
| `CN-A` | A 股（沪深） | 6 位数字代码（6xxxxx/0xxxxx/3xxxxx）、中文公司名、"股份有限公司" | IMA MCP 四个正文可读固定知识库 → 东方财富近 5 年卖方研报 → 妙想 skill A 股 → cn-web-search → WebSearch |
| `CN-FUND` | 公募基金 | 6 位代码以 0/1/5 开头、"基金"字样 | 妙想 skill 公募基金 → cn-web-search |
| `HK` | 港股 | 4-5 位数字代码、HKEX、港交所、中文/英文混合 | IMA MCP 四个正文可读固定知识库 → 东方财富近 5 年卖方研报 → 妙想 skill 港股 → cn-web-search → WebSearch |
| `US` | 美股 | 字母 ticker（AAPL, NVDA）、NYSE/NASDAQ、SEC filings | IMA MCP 四个正文可读固定知识库 → 东方财富近 5 年卖方研报 → 妙想 skill 美股 → WebSearch SEC → WebFetch EDGAR |
| `GLOBAL` | 跨市场主题 | 行业 / 宏观 / 主题类问题 | 并行多市场 |

## 市场识别规则

LLM 收到任务后，按以下顺序判断：

1. 用户明确指定市场 → 直接采用
2. 用户给出标的代码 → 按代码格式匹配（见上表）
3. 用户给出公司中文全名 → 默认 `CN-A`，若包含"港"/"HK"/"H 股"切 `HK`
4. 用户给出英文公司名或 ticker → 默认 `US`
5. 用户只说行业 / 主题 → `GLOBAL`，按 sm-industry-map 展开

## 合规分市场差异

- **CN-A / CN-FUND**：严格遵守 `compliance.md`，涉及评级、目标价、盈利预测调整必须提醒人工复核
- **HK**：注意公告延迟和信息披露差异
- **US**：SEC / 公司 IR 与妙想 skill 披露类数据作为事实锚，分析师报告默认归入 `市场共识`
- **GLOBAL**：跨市场对比必须注明不同会计准则、不同季度披露口径

## 不支持

以下市场暂不在 harness 覆盖范围内，遇到时明确告知用户：

- 数字货币 / 加密资产
- 未上市 / 一级市场 / PE/VC 标的
- 大宗商品期货（可通过妙想 skill 查指标但不做交易分析）
- 衍生品（期权、CDS 等）
