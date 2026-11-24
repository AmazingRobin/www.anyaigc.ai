# CLAUDE.md

@AGENTS.md

上面引入的 AGENTS.md 是本仓库的完整规则，做专题页前必须读完并按流程执行。以下是 Claude Code 专用的补充。

## 开工

- 用户说"做 <模型> 专题页"时，先按 AGENTS.md「1. 开工前向用户确认信息」逐项核对，缺的一次性问完，不要边做边问。
- 调研（官网风格、参考内容、接口文档、SEO 关键词）互相独立，并行用子代理做。
- 写完中文页再派子代理写英文页，同时自己做专题首页注册、sitemap、分享图。
- 中英文页和 SEO 后处理都做完、`check_topics.py` 0 错误之后，按 AGENTS.md「8. 新语言（ja/ko/es/de）」补日语、韩语、西班牙语、德语版本：翻译和复核用 `scripts/i18n/workflows/` 里的工作流并行，翻译者和复核者必须是不同的代理。用户没要求先做中英文时，不要把新语言留到"以后"：交付时明确告诉用户新语言做了没有。
- 工作流里用户说「暂停」之后，不要自己续跑，等用户说继续。

## 企业接入（每个专题页必须有）

AnyAIGC 的目标客户包括企业，**所有专题页都必须有企业接入版块**，新做的和已有的都一样。缺了 `check_topics.py` 会报错。

**中文页和非中文页（英文、日、韩、西、德）口径不同**（用户 2026-11-17 确认）：中文页写增值税发票、对公转账、合同；英文和新语言页只写「在控制台自助开具发票」，不写增值税、专票、对公转账、签订合同，也不写「中国大陆可访问」。`check_topics.py` 对非中文页会拦截 VAT、bank transfer、service agreement 这类说法。英文页写完后运行 `python scripts/i18n/overseas.py <前缀>` 自动改写（同时把前缀登记进 `overseas_done.json`，不登记就不检查）。

企业能力（已和用户确认，可以写）：

| 能力 | 中文写法 | 英文和新语言页写法 |
| :--- | :--- | :--- |
| 发票 | 增值税普通发票、增值税专用发票都能开，按实际充值金额开具 | Issue an invoice yourself in the console for the amount you actually topped up |
| 付款 | 支持企业对公转账充值 | 不写（支付方式只写 WeChat Pay / Alipay / USDT / Credit card） |
| 合同 | 可签订服务合同 | 不写 |
| 支持 | 专属客服和技术对接 | Dedicated support and technical contact |

**不要写**：SLA / 可用性承诺、企业专属分组或线路。用户明确要求不写。

**页面上任何位置都不要写令牌分组信息**（分组名称、"选择 Claude Code 分组 / 不要用默认分组"之类的提示），包括 Claude Code 版块和 FAQ。价格统一写模型广场的最低价，并注明实时价格以模型广场为准。

每个专题页要放这些位置：

1. **企业接入版块** `<section id="enterprise">`，放在快速开始/Claude Code 之后、平台优势或 FAQ 之前：
   - H2：中文「企业接入 <模型> API」，英文「<Model> API for teams and enterprises」
   - 中文页 4 张卡片：增值税发票 / 对公转账 / 签订合同 / 专属对接；**英文和新语言页只有 2 张：Self-service invoices（自助开票）/ Dedicated support**，没有对公转账和合同卡片
   - 主按钮「联系企业客服 / Talk to sales」→ `https://anyaigc.ai/customersupport`；次按钮「先注册试用 / Start with a free account」→ 注册链接
   - 样式跟随该页的模型品牌风格（Suno 用深色卡片，Claude 用象牙色卡片），不套统一模板
2. **导航**：加「企业接入 / Enterprise」→ `#enterprise`
3. **首屏要点或跑马灯**：中文页加一项「对公 · 专票」；英文和新语言页加「Self-service invoices」（不写 Contracts / VAT）
4. **meta description**：中文页写进对公转账、合同或增值税专票（优先「对公转账」「专票」）；英文和新语言页写 self-service invoices（各语言的对应说法）
5. **FAQ**（可见内容和 JSON-LD 同步）加两条：
   - 中文页：「AnyAIGC 能开发票吗？支持增值税专票吗？」「企业可以对公转账和签合同吗？」
   - 英文和新语言页：只有一条「Can I get an invoice from AnyAIGC?」（答案：可以在控制台自助开具，按实际充值金额），没有对公转账和合同那一条
6. **keywords**：中文页加「<模型> API 企业」「<模型> API 发票」；英文页加「<Model> API for business」
7. 不要再用「企业用户可联系客服确认发票方案」这类含糊说法，直接写支持对公转账和增值税发票。

## 支付方式（每个专题页必须有）

支持的支付方式：**微信支付、支付宝、USDT、信用卡**，中文页另写企业对公转账。英文和新语言页写 WeChat Pay / Alipay / USDT / Credit card，**不写 Bank transfer**。

- 企业接入版块里放一行支付方式徽标（`.pay-row`，样式在 `scrollbar.css`），FAQ 加一条「支持哪些支付方式？」（可见内容和 JSON-LD 同步）。
- 新页面写完后运行 `python scripts/payments.py` 自动补上，脚本重复运行结果不变。缺了 `check_topics.py` 会报错。

## 信任与保障（每个专题页必须有）

用户 2026-10-24 确认属实、可以写的信任信息，**只写这些，不要自行扩展**：

| 项 | 中文写法 | 英文写法 |
| :--- | :--- | :--- |
| 试用 | 新用户注册送 200 万 tokens 试用额度 | 2M free tokens for new accounts |
| 充值 | $1 起充 | Top up from $1 |
| 退款 | 未使用余额可退款，无手续费 | Unused balance refundable, no fee |
| 渠道 | 官方模型渠道，不掺假不降智（不用低配/逆向模型冒充） | Official model channels, no substitutes |
| 数据 | 除法律法规要求外，不对输入输出做持久化存储、不用于训练（与隐私政策 1.2 一致，链接 /privacy） | No persistent storage of prompts/outputs, no training |
| 账单 | 控制台可查每次调用的 tokens 与扣费明细，可给每个 Key 设额度上限 | Per-request usage log, per-key spend caps |
| 客服 | 7×24 客服，链接 https://anyaigc.ai/customersupport（不写具体微信号/Telegram） | 24/7 support |

不要写：SLA/可用率、企业专属分组/线路、令牌分组、用户数/成立年限/官方合作关系（没有确认的数字一律不写）。

- 版块 `section#trust`（「为什么可以放心用 AnyAIGC」），放在企业接入之后，6 项清单（`.trust-list`，样式在 `scrollbar.css`）+「先注册领取 200 万 tokens」按钮；FAQ 加 3 条：免费试用额度 / 余额退款 / 是否掺假与数据安全。
- 新页面写完后运行 `python scripts/trust.py` 自动补上（重复运行结果不变，改文案后重跑会整体替换）。缺了 `check_topics.py` 会报错。

## 工具

- 本地预览：`python scripts/preview.py`（后台运行），不要用 `python -m http.server`。
- 自检：`PYTHONIOENCODING=utf-8 python scripts/check_topics.py`，0 错误才能交付。
- Playwright MCP 截图路径必须在仓库内，用 `.playwright-mcp/`，交付前删除截图。
- `docs.anyaigc.ai` 是 JS 渲染的，用 Playwright `browser_navigate` + `browser_evaluate` 读 `main.innerText`。

## 交付

- 不要自动 commit 或 push，等用户要求。
- 回复里说明：新增/修改了哪些文件、自检结果、需要用户确认的事实、预览地址。
