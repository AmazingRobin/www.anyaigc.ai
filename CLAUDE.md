# CLAUDE.md

@AGENTS.md

上面引入的 AGENTS.md 是本仓库的完整规则，做专题页前必须读完并按流程执行。以下是 Claude Code 专用的补充。

## 开工

- 用户说"做 <模型> 专题页"时，先按 AGENTS.md「1. 开工前向用户确认信息」逐项核对，缺的一次性问完，不要边做边问。
- 调研（官网风格、参考内容、接口文档、SEO 关键词）互相独立，并行用子代理做。
- 写完中文页再派子代理写英文页，同时自己做专题首页注册、sitemap、分享图。

## 企业接入（每个专题页必须有）

AnyAIGC 的目标客户包括企业，**所有专题页（中英文）都必须包含企业开票/对公转账信息**，新做的和已有的都一样。缺了 `check_topics.py` 会报错。

企业能力（已和用户确认，可以写）：

| 能力 | 中文写法 | 英文写法 |
| :--- | :--- | :--- |
| 发票 | 增值税普通发票、增值税专用发票都能开，按实际充值金额开具 | Invoices for every top-up, including Chinese VAT general and special invoices |
| 付款 | 支持企业对公转账充值 | Corporate bank transfer |
| 合同 | 可签订服务合同 | Service agreement |
| 支持 | 专属客服和技术对接 | Dedicated support and technical contact |

**不要写**：SLA / 可用性承诺、企业专属分组或线路。用户明确要求不写。

**页面上任何位置都不要写令牌分组信息**（分组名称、"选择 Claude Code 分组 / 不要用默认分组"之类的提示），包括 Claude Code 版块和 FAQ。价格统一写模型广场的最低价，并注明实时价格以模型广场为准。

每个专题页要放这些位置：

1. **企业接入版块** `<section id="enterprise">`，放在快速开始/Claude Code 之后、平台优势或 FAQ 之前：
   - H2：中文「企业接入 <模型> API」，英文「<Model> API for teams and enterprises」
   - 4 张卡片：增值税发票 / 对公转账 / 签订合同 / 专属对接（英文 Invoices / Bank transfer / Contracts / Dedicated support）
   - 主按钮「联系企业客服 / Talk to sales」→ `https://anyaigc.ai/customersupport`；次按钮「先注册试用 / Start with a free account」→ 注册链接
   - 样式跟随该页的模型品牌风格（Suno 用深色卡片，Claude 用象牙色卡片），不套统一模板
2. **导航**：加「企业接入 / Enterprise」→ `#enterprise`
3. **首屏要点或跑马灯**：加一项「对公 · 专票」/「Contracts · invoices」
4. **meta description**：写进对公转账、合同或增值税专票（中文页优先「对公转账」「专票」）
5. **FAQ**（可见内容和 JSON-LD 同步）加两条：
   - 「AnyAIGC 能开发票吗？支持增值税专票吗？」/「Can AnyAIGC issue invoices, including VAT special invoices?」
   - 「企业可以对公转账和签合同吗？」/「Can my company pay by bank transfer and sign a contract?」
6. **keywords**：加「<模型> API 企业」「<模型> API 发票」/「<Model> API for business」
7. 不要再用「企业用户可联系客服确认发票方案」这类含糊说法，直接写支持对公转账和增值税发票。

## 工具

- 本地预览：`python scripts/preview.py`（后台运行），不要用 `python -m http.server`。
- 自检：`PYTHONIOENCODING=utf-8 python scripts/check_topics.py`，0 错误才能交付。
- Playwright MCP 截图路径必须在仓库内，用 `.playwright-mcp/`，交付前删除截图。
- `docs.anyaigc.ai` 是 JS 渲染的，用 Playwright `browser_navigate` + `browser_evaluate` 读 `main.innerText`。

## 交付

- 不要自动 commit 或 push，等用户要求。
- 回复里说明：新增/修改了哪些文件、自检结果、需要用户确认的事实、预览地址。
