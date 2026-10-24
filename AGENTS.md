# AGENTS.md

本仓库是 AnyAIGC 的官网落地页与模型专题页，纯静态 HTML/CSS/JS，部署在 Cloudflare Pages。本文件是做专题页的规则和流程，新增或修改专题页时必须遵守。

## 项目速览

- 站点域名：`https://www.anyaigc.ai`（本仓库，canonical、sitemap、og:url 都用它）
- 平台与 API 地址：`https://anyaigc.ai`（注册、控制台、模型广场、API 调用）
- API 文档：`https://docs.anyaigc.ai`
- 无构建步骤、无框架、无 npm 依赖。不要引入框架、打包工具或外部 CDN 字体/脚本。
- Cloudflare Pages 自动去掉 `.html`：`/zh/models/suno.html` 对外地址是 `/zh/models/suno`。

```
zh/models/index.html      中文专题首页（所有中文专题的列表）
zh/models/<slug>.html     中文专题页
en/models/index.html      英文专题首页
en/models/<slug>.html     英文专题页
assets/models/scrollbar.css   所有专题页共用的滚动条样式（必须引入）
assets/models/hub.css         专题首页样式（沿用站点首页 af-* 风格）
assets/models/<slug>.css      每个专题页自己的样式
assets/models/<slug>.js       每个专题页自己的交互（可选）
assets/og/<slug>-zh.png       分享图 1200×630，中英各一张
sitemap.xml / robots.txt / _headers
scripts/preview.py        本地预览（模拟 Cloudflare clean URL）
scripts/check_topics.py   专题页自检
```

同一厂商的系列模型共用一套样式和脚本：Claude 用 `assets/models/claude.css`、`claude.js`（总览页另加 `claude-hub.css`）；GPT 用 `assets/models/gpt.css`、`gpt.js`（OpenAI 深色风格，总览页 `/models/gpt` 也用它）。GPT 分享图用 `python scripts/og_gpt.py` 生成。GPT-6 系列在 Chat Completions 上的工具调用有限制，代码示例里工具调用一律走 `/v1/responses`；gpt-5.5-pro 只支持 Responses API。系列页面底部有「同系列模型」列表（`section#family`，放在 FAQ 前），新增或下线一个系列模型时，要同步更新该系列所有页面的列表、专题首页对应分类、sitemap。旧版模型（官方标为 Legacy）首屏加 `.o-notice` 提示并链接到替代型号，FAQ 加一条「停用了吗」。

`<slug>` 用小写短横线，和模型官方名对齐，例如 `suno`、`gpt-5`、`claude-opus-4-5`。中英文用同一个 slug。

## 固定信息（所有页面统一）

| 项 | 值 |
| :--- | :--- |
| 平台名 | AnyAIGC |
| 平台模型数 | 300+（不要写 500+ 或其他数字） |
| 注册链接 | `https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9`（所有注册按钮都用这个，参数不能丢） |
| 模型广场 | `https://anyaigc.ai/pricing` |
| 控制台 / 登录 | `https://anyaigc.ai/console` |
| 联系客服 | `https://anyaigc.ai/customersupport` |
| 鉴权方式 | `Authorization: Bearer <API Key>` |
| 计价货币 | USD |
| 企业服务 | 增值税普票/专票、对公转账、签订合同、专属客服与技术对接（每个专题页必须写；不写 SLA、企业专属分组/线路） |

## 工作流程

### 1. 开工前向用户确认信息

用户通常会按 [TOPIC_BRIEF.md](TOPIC_BRIEF.md) 模板发来需求。逐项核对必填项，缺的一次性问完。以下信息不能猜，没拿到之前不要写价格和代码：

- 模型在 AnyAIGC 上的模型名（如 `suno_music_open`）
- 固定价格表：每个功能/操作的单价
- 接口路径和文档链接（`docs.anyaigc.ai` 上对应页面）
- 并发限制（RPM），以及是否所有用户默认享有
- 一次调用的产出（例如 Suno 发起创作一次返回 1 首）
- 风格参考站（通常是模型官网）和内容参考页
- 是否有特殊卖点或不能写的内容

### 2. 调研

- 风格：打开模型官网，提取配色（具体 hex）、字体、圆角、按钮、卡片、版块顺序、动效。截图存到 `.playwright-mcp/`（已在 .gitignore）。
- 内容：读参考页的完整内容，把平台换成 AnyAIGC，按我们的价格和接口重写，不要整段照抄。
- 接口：以 `docs.anyaigc.ai` 为准。文档是 JS 渲染的，WebFetch 拿不到内容时用 Playwright 读 `main.innerText`。代码示例里的路径、字段、返回格式必须和文档一致，不能沿用竞品的接口结构。
- 版本：从文档里确认支持的模型版本，写进标题和 FAQ。
- SEO：搜中英文关键词（"<模型> API"、"<模型> API 价格"、"<模型> API key"、"<model> API pricing" 等），看排名靠前的页面标题和用户常问的问题。

### 3. 写中文页 `zh/models/<slug>.html`

结构见下面的「专题页规则」。

### 4. 写英文页 `en/models/<slug>.html`

本地化改写，不是逐句翻译。价格、模型名、接口、代码结构保持一致，代码注释和示例提示词换成英文。

### 5. 注册到专题首页和 sitemap

- `zh/models/index.html` 和 `en/models/index.html`：在对应类别的 `<ul class="af-models">` 里加一张 `af-model` 卡片；没有合适类别就新建一个类别标题 + 筛选链接。
- 两个专题首页的 JSON-LD `ItemList`：加 `ListItem`，`position` 顺延，更新 `numberOfItems`。
- `sitemap.xml`：中英各加一个 `<url>`，带三条 `xhtml:link`（zh-CN / en / x-default），更新 `lastmod`。
- 专题首页本身的 `lastmod` 也改成当天。

### 6. 分享图

做 1200×630 的 `assets/og/<slug>-zh.png` 和 `<slug>-en.png`：写一个临时 HTML，用 Playwright 截图。风格跟专题页一致，内容是模型名 + 一句卖点 + 3–4 个标签。临时 HTML 用完删掉。Claude 系列用 `python scripts/og_claude.py` 生成源文件（副标题在脚本的 `SUBS` 里维护）。

**品牌名必须写成 `AnyAIGC`（区分大小写）**，分享图、导航、页脚都一样，不要用 `text-transform:uppercase` 或写成 `ANYAIGC`。（环境变量名 `ANYAIGC_API_KEY` 是代码，不受此限制。）

### 7. 验证（必须做完再交付）

```bash
python scripts/preview.py            # http://localhost:8765/zh/models/<slug>
PYTHONIOENCODING=utf-8 python scripts/check_topics.py
```

- `check_topics.py` 必须 0 错误。它会检查 title/description、canonical、hreflang、OG、JSON-LD、FAQ 条数一致、站内链接、scrollbar.css 引入与滚动条品牌色变量、注册链接参数、企业接入版块/导航/description/FAQ、中英对称、专题首页与 sitemap 注册。
- 用 Playwright 在 1440×900 和 390×844 截全页，确认：没有 JS 报错、手机端 `scrollWidth` 不超过视口、价格表在手机上可读。
- 点一次语言切换链接，确认中英互跳正常。
- 不要用 `python -m http.server` 预览，它不支持 clean URL，`/en/models/<slug>` 会 404。

### 8. 交付

告诉用户改了哪些文件、需要他确认的事实（例如文档里没写清楚的返回字段）、本地预览地址。不要自动提交或推送。

## 专题页规则

### 视觉

- **每个专题页按该模型官网的风格单独设计，不套固定模板。** 配色、字体气质、版块节奏都参考官网。样式写在 `assets/models/<slug>.css`，类名用模型专属前缀（Suno 用 `s-`），避免和其他专题冲突。
- 不使用专辑封面、产品截图、插画等素材，用 CSS 渐变、SVG、波形等自己画。
- **模型 logo 一律用 lobe-icons，不要自己画**（MIT 协议，https://github.com/lobehub/lobe-icons ，图标检索 https://lobehub.com/zh/icons ）。
  - 下载固定版本的 SVG 到 `assets/icons/<id>.svg`（地址 `https://registry.npmmirror.com/@lobehub/icons-static-svg/<版本>/files/icons/<id>.svg`，版本号写在 `scripts/icons.py` 的 `VERSION`）。有 `-color` 彩色版就用彩色版（如 `claude-color`），没有就用单色版并在 SVG 上写 `fill`（如 `suno` 在深色页用白色）。
  - 新模型：把 id 加进 `scripts/icons.py` 的 `ICONS`，运行 `python scripts/icons.py --fetch`，再在脚本里加对应页面的替换规则。脚本把 path 内联进页面（首屏、结尾、专题首页卡片），重复运行结果不变。
  - 分享图用同一份 SVG（`scripts/og_claude.py` 读 `assets/icons/claude-color.svg`）。
  - 页脚商标声明照常保留。
- 专题首页（`/zh/models/`、`/en/models/`）统一用 `hub.css`，沿用站点首页的 af-* 暖色风格，不按模型变。
- **滚动条必须换成该模型的品牌色。** 所有专题页 `<head>` 里先引入 `/assets/models/scrollbar.css`（只提供圆角、尺寸和中性默认色），再引入页面自己的 CSS，并在自己的 CSS 里覆盖全部 4 个变量：
  - 浅色页面：写在 `:root{...}` 里
  - 深色页面：`<html>` 加 `data-scrollbar="dark"`，变量写在 `:root[data-scrollbar="dark"]{...}` 里

  ```css
  /* 示例：Suno（深色，渐变滑块） */
  :root[data-scrollbar="dark"]{
    --sb-track:#101012;                 /* 轨道，通常等于页面背景色 */
    --sb-thumb:#e8502a;                 /* 纯色，Firefox 用 */
    --sb-thumb-bg:linear-gradient(180deg,#ffb003,#e8502a 55%,#fe3c7d); /* 滑块，可用渐变 */
    --sb-thumb-hover:linear-gradient(180deg,#ffc43d,#f0603a 55%,#ff5a92); /* 悬停 */
  }
  ```

  颜色从模型官网的主色/强调色里取，轨道色和页面背景一致。不要在页面里设置 `scrollbar-color`，Chrome 121+ 设置它后会忽略 `::-webkit-scrollbar` 的圆角和渐变。`check_topics.py` 会检查这 4 个变量是否齐全。
- 资源和站内链接一律用 `/` 开头的绝对路径。站内链接不带 `.html`。
- `/assets/models/` 下的 CSS/JS 引用都带版本号 `?v=YYYYMMDD`（例 `/assets/models/suno.css?v=20261022`）。改了某个 CSS/JS，就把所有引用它的页面里的版本号改成当天日期，否则浏览器和 Cloudflare 会继续用缓存里的旧文件。
- 页面里如果设置了全局 `::selection` 文字颜色，深色区域（页脚、深色结尾、代码块、深色按钮/标签）必须单独设置浅色选中样式，否则深底深字看不清。
- 关键颜色（品牌色、logo 填充）直接写在 SVG 的 `fill` 属性上，不要只靠外部 CSS，避免样式缓存或加载失败时颜色不对。
- 必须支持 `prefers-reduced-motion`，动画在该模式下关闭。
- 响应式断点至少覆盖 1100 / 900 / 640px，手机端不能横向溢出。

### 版块（按需取舍，顺序可调）

1. 导航：品牌、模型专题、模型广场、本页价格锚点、API 文档、语言切换、登录、注册
2. 首屏：面包屑、要点标签、H1（含"<模型> API"）、一句话说明（含起步价）、主按钮"获取 API Key"
3. 功能：模型能做什么，每项一张卡片
4. **价格**（见下）
5. 使用场景
6. 平台优势：300+ 模型一个 Key、国内直连、固定价格、并发
7. 快速开始：三步 + cURL / Python 示例
8. **企业接入（必须有）**：`<section id="enterprise">`，增值税普票/专票、对公转账、签订合同、专属客服与技术对接，主按钮联系企业客服。完整要求见 CLAUDE.md「企业接入」。不写 SLA 和企业专属分组/线路。
9. FAQ：8–12 条，其中必须包含开票（增值税专票）和对公转账/合同两条
10. 结尾 CTA + 相关链接（专题首页、模型广场、文档、另一语言版本）
11. 页脚：免责声明"<模型> 是 <公司> 的商标，AnyAIGC 是独立 API 服务商，与其无隶属关系"

### 价格版块

- **按 API 价格表展示，不要做成订阅套餐卡片**（不要"套餐 A/B/C"、"最受欢迎"角标、每卡一个按钮、"$x 起"）。
- 用一张 `<table>`：功能 | 模型名 | 单价（USD）；用 `<tbody>` 按功能分组，免费项写"免费 / Free"。
- 表格上方放计费要点条（按次计费、一次产出多少、并发、余额通用）。
- 表格下方放 2–3 个成本示例，用真实单价相加算出结果，写在 HTML 里，不用 JS 计算。
- 整个版块只放一个主按钮"获取 API Key"，一个次链接"在模型广场查看"。
- 价格底注：单位 USD，按成功提交计费，实时价格以模型广场为准。
- 价格只用用户给的数字，不要四舍五入改写；JSON-LD Offer、FAQ 里的价格必须和表格一致。

### 代码示例

- 接口地址、字段、返回格式以 `docs.anyaigc.ai` 为准。
- Key 从环境变量 `ANYAIGC_API_KEY` 读，不写死。
- Python 代码要能直接运行：字符串里的换行写成 `\n`，不要在字符串里真的换行。
- 文档没写清楚的字段（如任务状态值）在交付时告诉用户需要确认。

### 内容

- 不编造事实：价格、并发、版本、产出数量都来自用户或文档。拿不准的问用户。
- 不写"最好、最强、第一"这类绝对化用语。
- 涉及商用授权，写"以 <模型厂商> 官方条款为准"。
- 中文用简体，英文用美式英语。

## SEO 清单

每个专题页都要有：

- `<html lang>`：中文 `zh-CN`，英文 `en`
- `<title>`：英文 ≤ 65 字符；中文显示宽度 ≤ 64（汉字计 2）。格式："<模型> API 价格与接入｜<卖点> - AnyAIGC"
- `meta description`：英文 120–160 字符，中文 60–120 字，包含模型名、起步价、核心能力、并发
- `meta robots`：`index,follow,max-image-preview:large`
- `canonical`：自身的 www 地址，不带 `.html`
- `hreflang`：`zh-CN`、`en`、`x-default`（指向英文）三条，中英页面互相声明
- Open Graph：`og:type`、`og:site_name`、`og:locale` + `og:locale:alternate`、`og:url`、`og:title`、`og:description`、`og:image`（含宽高和 alt）
- Twitter：`summary_large_image` + title/description/image
- 唯一一个 `<h1>`，H2 覆盖主要关键词（价格、接入、FAQ）
- JSON-LD（`@graph`）：
  - 专题页：`Organization`、`WebSite`、`WebPage`、`BreadcrumbList`、`Product`（`AggregateOffer` + 每个价格一个 `Offer`）、`FAQPage`
  - 专题首页：`CollectionPage`、`BreadcrumbList`、`ItemList`
  - FAQPage 的问题和回答必须和页面上可见的 FAQ 逐条一致（条数也一致）
- 价格表、FAQ、代码都直接写在 HTML 里，不依赖 JS 渲染
- 可见的面包屑导航，和 BreadcrumbList 对应
- 内部链接：专题页 ↔ 专题首页 ↔ 站点首页互相链接，语言切换用 `hreflang` 属性

## 常见坑

- Windows 下 Python 打印中文会乱码，运行脚本前设 `PYTHONIOENCODING=utf-8`。写文件时用 `encoding='utf-8'`。
- 用 bash heredoc 写含单引号的长内容容易出错，复杂内容用 Write 工具写成文件再处理。
- Playwright 截图只能保存到仓库目录（如 `.playwright-mcp/`），交付前删掉截图。
- 改了全站文案（如模型数、注册链接）要同时改 `index.html`、`privacy.html`、`terms.html`、`README.md`、`README.en.md` 和所有专题页。
