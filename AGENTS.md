# AGENTS.md

本仓库是 AnyAIGC 的官网落地页与模型专题页，纯静态 HTML/CSS/JS，部署在 Cloudflare Pages。本文件是做专题页的规则和流程，新增或修改专题页时必须遵守。

## 项目速览

- 站点域名：`https://www.anyaigc.ai`（本仓库，canonical、sitemap、og:url 都用它）
- 平台与 API 地址：`https://anyaigc.ai`（注册、控制台、模型广场、API 调用）
- API 文档：`https://docs.anyaigc.ai`
- 无构建步骤、无框架、无 npm 依赖。不要引入框架、打包工具或外部 CDN 字体/脚本。
- Cloudflare Pages 自动去掉 `.html`：`/zh/models/suno.html` 对外地址是 `/zh/models/suno`。

```
index.html                站点首页（中文），en/ ja/ ko/ es/ de/ 下各有 index.html。由 scripts/home_page.py 生成，不要手改
scripts/home_page.py      站点首页生成脚本；文案在 scripts/home_copy/<lang>.json，样式 assets/home/home.css，脚本 assets/home/home.js
zh/models/index.html      中文专题首页（所有中文专题的列表）
zh/models/<slug>.html     中文专题页
en/models/index.html      英文专题首页
en/models/<slug>.html     英文专题页
assets/models/scrollbar.css   所有专题页共用的滚动条样式（必须引入）
assets/models/hub.css         专题首页样式（与站点首页同一套暖黑配色，见下方「站点视觉」）
legal.css                     隐私政策、服务条款、404 的样式（同一套配色）
privacy.html / terms.html     隐私政策、服务协议的中文原文（法律文本，唯一的源）；en/ ja/ ko/ es/ de/ 下的同名页由 scripts/legal_pages.py 生成，不要手改
scripts/legal_copy/<lang>.json  法律页译文（src.json 是中文原文抽出的单元）；改了中文原文要先 `python scripts/legal_pages.py extract`，重新翻译变化的单元，再 `build`
assets/models/<slug>.css      每个专题页自己的样式
assets/models/<slug>.js       每个专题页自己的交互（可选）
assets/og/<slug>-zh.png       分享图 1200×630，中英各一张
sitemap.xml / robots.txt / _headers
scripts/preview.py        本地预览（模拟 Cloudflare clean URL）
scripts/check_topics.py   专题页自检
```

同一厂商的系列模型共用一套样式和脚本：Claude 用 `assets/models/claude.css`、`claude.js`（总览页另加 `claude-hub.css`）；GPT 用 `assets/models/gpt.css`、`gpt.js`（OpenAI 深色风格，总览页 `/models/gpt` 也用它）。GPT 分享图用 `python scripts/og_gpt.py` 生成。GPT-6 系列在 Chat Completions 上的工具调用有限制，代码示例里工具调用一律走 `/v1/responses`；gpt-5.5-pro 只支持 Responses API。Jev（TypeSafe）系列共用 `assets/models/jev.css`、`jev.js`，分享图用 `python scripts/og_jev.py` 生成；Jev 走 `POST /v1/systemone`，不是 OpenAI 兼容接口。系列页面底部有「同系列模型」列表（`section#family`，放在 FAQ 前），新增或下线一个系列模型时，要同步更新该系列所有页面的列表、专题首页对应分类、sitemap。旧版模型（官方标为 Legacy）首屏加 `.o-notice` 提示并链接到替代型号，FAQ 加一条「停用了吗」。

`<slug>` 用小写短横线，和模型官方名对齐，例如 `suno`、`gpt-5`、`claude-opus-4-5`。中英文用同一个 slug。

## 固定信息（所有页面统一）

| 项 | 值 |
| :--- | :--- |
| 平台名 | AnyAIGC |
| 平台模型数 | 300+（不要写 500+ 或其他数字） |
| 注册链接 | `https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9`（所有注册按钮都用这个，参数不能丢） |
| 模型广场 | `https://anyaigc.ai/pricing` |
| 价格快照 | `drafts/pricing.json`（全部模型的最低价和各分组价，已被 .gitignore 忽略）。查价格先 `python scripts/pricing_dump.py <模型名子串>`（读本地文件），数据旧了或要核对时先 `python scripts/pricing_dump.py` 重新拉取（直接调 `/api/pricing`，不用开浏览器）。两个已知差异：个别按量价第 4 位小数会比弹窗差 0.0001（例如 Codex-Gpt-2 的输出价弹窗是 $2.4710，文件里是 $2.4709），页面上以模型广场弹窗显示为准；视频和音频的分档倍率在文件的 `raw` 里。 |
| 人民币换算 | 按张价格显示人民币时 = 美元价 × 6.7（`gpt_image_data.RMB_RATE`，用户 2026-11-25 指定），标红；按量价格保持美元 |
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
- 日语、韩语、西班牙语、德语的专题首页和 sitemap 条目在第 8 步「新语言」里补，这里只做中英。

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
- 页面写完后，按下面「SEO 后处理脚本」的顺序补跑一遍，再跑 `check_topics.py`。新页的标题、同类模型版块会由这些脚本补上，不用手写。
- 不要用 `python -m http.server` 预览，它不支持 clean URL，`/en/models/<slug>` 会 404。

### 8. 新语言（ja/ko/es/de）

中文页和英文页做完、「SEO 后处理脚本」跑完、`check_topics.py` 0 错误之后，再做日语、韩语、西班牙语、德语版本。**以英文页为源，不是中文页。** 站点已有 6 种语言（zh、en、ja、ko、es、de），新增的专题页也要补齐，否则这几种语言的用户在语言菜单里会看到页面缺失。`check_topics.py` 会对缺少新语言版本的专题页给出警告（不是错误，可以按系列分批做）：交付时要告诉用户哪些没做、打算什么时候做。

**口径（用户已确认，英文页和新语言页一样适用）：**

- 发票只写「在控制台自助开具，按实际充值金额开具」。不写增值税、专票、对公转账、签订合同、中国大陆可访问、国内直连、海外信用卡。保留微信支付、支付宝、USDT、信用卡，保留「专属客服与技术对接」。
- 价格和小数一律用小数点（`$0.0596`），德语、西语也不用逗号。
- 品牌名 `AnyAIGC`；代码、模型 ID、URL、数字原样保留，翻译只动文字。
- 翻译者和复核者必须是不同的代理；不自动 commit；用户说「暂停」之后不要自己续跑工作流。

**步骤**（S = 这批页面的 slug，P = slug 前缀；单个新型号也当作一个"系列"来做，翻译记忆库会复用已有译文，通常只剩少量待译条目。各脚本的细节和参数见 `scripts/i18n/README.md`）：

```bash
export PYTHONIOENCODING=utf-8
python scripts/i18n/overseas.py P                  # 1 英文页改成海外口径（自动登记进 overseas_done.json；不登记 check_topics 就不检查这个前缀）
python scripts/i18n/china_faq.py P                 #   删掉「能否从中国大陆调用」的 FAQ
python scripts/i18n/china_body.py P                #   删掉正文里的大陆直连说法
python scripts/check_topics.py                     #   英文页仍要 0 错误
python scripts/i18n/merge_tm.py <系列> --all       # 2 合并所有已有的翻译记忆库
python scripts/i18n/batch.py prepare <系列> S      # 3 合并去重
python scripts/i18n/batch.py tm-fill <系列> <lang> #   每种语言各跑一次，命中记忆库的直接用
python scripts/i18n/batch.py tm-chunks <系列> 11000
#   把 drafts/i18n/<系列>/chunks/*.json 复制成 todo/<lang>-<NN>.json（每种语言一份，翻译工作流读的是 todo/）
#   4 翻译：scripts/i18n/workflows/translate-group.js（args：series chunks wave brief desc refs），写出 out/<lang>-todo-<NN>.json
#   然后每种语言 python scripts/i18n/consolidate.py <系列> <lang> 合成 out/<lang>-all.json
#   复核：scripts/i18n/workflows/review-segmented.js（按 id 段并行，写 out/<lang>-rev-<seg>.json 补丁；check_patch.py 通过、补丁文件 90 秒没变化后 merge_patches.py）
#   简报：scripts/i18n/briefs/ 里按系列写一份术语表和语气（可复制最近的 batch*.md 改）
python scripts/i18n/batch.py validate <系列> <lang>   # 5 校验，ERROR 必须为 0
python scripts/i18n/batch.py render <系列> <lang> S   # 6 渲染成 <lang>/models/<slug>.html
python scripts/i18n/register.py S                  # 7 sitemap，并给中英页补 hreflang 和语言菜单
python scripts/i18n/decimal_point.py html          # 8 保证 es/de 没有小数逗号
python scripts/i18n/relink_home.py                 # 9 首页、隐私政策、服务条款的链接指向各语言自己的页面
python scripts/i18n/org_logo.py                    #   结构化数据里的 logo
python scripts/og_<系列>.py --langs=ja,ko,es,de    # 10 分享图（先给脚本加四种语言文案；出图后核对每张的修改时间，Chrome 偶发静默失败会写回旧图）
python scripts/related_models.py                   # 11 同类模型版块
python scripts/sitemap_lastmod.py
python scripts/check_topics.py                     # 12 必须 0 错误，不再有「缺少 x 版本」的警告
```

- **专题首页（4 种新语言）要补卡片：** `index` 当作一个页面走同样的流程：`batch.py prepare hub index`，`resync.py hub`，补译缺口，`render hub <lang> index`。新增型号后这一步容易漏。
- **英文页以后又改了，要重新同步：** 先 `prepare`，再 `resync.py <系列>`，补译 `todo-resync-<lang>.json`，再渲染。重新运行任何 `*_pages.py` 生成脚本后，英文页会回到旧写法：要重跑 `overseas.py`、`china_faq.py`、`china_body.py`、`relink_home.py`、`org_logo.py`。
- **版面检查：** 日语和德语各一页，在 390px 宽下量 `scrollWidth`（`scripts/i18n/mobile_probe.py`），别大量截图。
- 站点首页（`/`、`/en/` 等）、隐私政策、服务条款不是每次新增型号都要动。改它们见上面「项目速览」里的 `scripts/home_page.py` 和 `scripts/legal_pages.py`。

### 9. 交付

告诉用户改了哪些文件、需要他确认的事实（例如文档里没写清楚的返回字段）、本地预览地址。不要自动提交或推送。

## SEO 后处理脚本（生成页面后必须按顺序补跑）

各系列的生成器（`scripts/<系列>_pages.py` 等）输出的是原始页面。下面这些脚本在生成之后再改 HTML。**新增一个型号页，或重新生成某个系列之后，必须按下面的顺序补跑**，否则标题、规格版块、同类模型、结构化数据会回到生成器的旧写法。每个脚本重复运行都不会产生新改动，带 `--dry-run` 的只预演不写文件。

```bash
export PYTHONIOENCODING=utf-8
python scripts/seo_titles.py            # 1  标题补卖点；快速开始 H2；Qwen 子页关键词和 FAQ；海外模型中文关键词
python scripts/seo_overview_titles.py   # 2  系列总览页专用标题
python scripts/seo_title_selling.py     # 3  中文标题写「约官方 X 折」（读页面里已有的折扣）
python scripts/seo_titles_en_save.py    # 4  英文标题写 Save X%（折扣取自第 3 步的中文标题）
python scripts/seo_title_names.py       # 5  标题去掉 Preview、补全日期
python scripts/seo_unique.py            # 6  Qwen 对话页的规格版块
python scripts/seo_unique_media.py      # 7  Speech、HappyHorse 的规格版块和 FAQ
python scripts/seo_unique_specs.py      # 8  其余系列的规格版块（数据在 scripts/seo_specs_data.json）
python scripts/seo_overview_faq.py      # 9  Qwen、Kling 总览页的价格 FAQ
python scripts/seo_offers.py            # 10 JSON-LD 里去掉价格为 0 的免费项
python scripts/related_models.py        # 11 「同类模型 API」版块
python scripts/check_topics.py          # 12 自检，必须 0 错误
```

最后运行 `python scripts/sitemap_lastmod.py`，把 `sitemap.xml` 和内容放进同一个提交。提交前后都可以跑：正文和最新提交不同的页面，或 git 还没见过的新页面，写今天的日期；正文和最新提交一致的页面，写最后一次改动它的提交日期。只改版本号、`<head>` 或结构化数据，不算正文变化，不会改动日期。脚本要逐个页面比对提交历史，全站大约需要 2 分钟。

**顺序有依赖，不能打乱：** 第 3 步读第 1 步写好的标题；第 4 步读第 3 步的折扣，必须在它之后；第 5 步最后动标题，避免被前面的脚本改回去。Llama 的规格版块直接写在 `llama_pages.py` 里，不在上面的列表中。

### 新型号要给这些脚本提供什么

- **规格版块**：在 `scripts/seo_specs_data.json` 加一条记录（`slug`、`source` 官方链接、`facts_zh`、`facts_en`，可选 `compare_slug`/`compare_zh`/`compare_en`）。**事实只写在厂商官网读到的内容**，上下文、最大输出、参数规模这类数字必须有出处。读不到官方资料就不写，页面保持没有这个版块，不要凭记忆或第三方站点补。价格不用写，脚本从页面自己的价格表读。
- **同类模型**：新厂商或新类别要在 `scripts/related_models.py` 的 `TARGETS` 里加一项，并在 `category()` 的前缀表里归类。
- **折扣**：中文标题只在页面上已有「约官方 X 折」或「比官方便宜 X%」这类对比官方价的说法时才写折，否则保留起步价；只写「68 折」这种活动标签不算。
- 厂商文档如果已把型号标为停用或旧版，事实里不写停用日期，先问用户 AnyAIGC 是否还在提供。

### 标题卖点规则（脚本按此生成，手写标题要保持一致）

- 中文：`<模型> API 价格与接入｜约官方 X 折 - AnyAIGC`；没有对比官方价的折扣就写起步价，例如 `｜$0.0304/百万 tokens 起`。系列总览页写「最低约官方 X 折」。不在标题里写「中转」，它只放在 meta keywords。
- 英文：有折扣写 `Save X%`（不用「折」的说法），没有写 `From $X/1M tokens`。
- 标题里用常见产品名：`Gemini 3.1 Pro`，不带 `Preview`；H1、正文和代码示例保留完整模型 ID，因为调用接口要用准确的名字。模型名本身就是原始 ID（如 `doubao-seed-2-1-pro`）的不缩短。
- 英文标题 ≤ 65 字符（按转义后计），中文显示宽度 ≤ 64。放不下时脚本只压缩单位和空格（`/百万 tokens` → `/M`），不删价格。

### 已知缺口（脚本没覆盖，重新生成会丢）

- Qwen、万相、HappyHorse 页面的可见面包屑（`.q-crumb`）和可灵页面里的「Kling 系列总览」一层，是一次性补丁写入的，没有进生成器。重新生成这些系列后要补回，并让 `BreadcrumbList` JSON-LD 和可见内容一致。
- 首页的「热门模型 API」版块和 `functions/[[path]].js`（拦截内部文件）是手写的。
- 官方已下线或标为旧版的型号（豆包 Seed 1.6/1.8、MiMo V2.5、Kimi K2.6/K2.7 Code、Claude 的 Legacy 型号等）的页面写法，要先确认 AnyAIGC 是否还在提供再决定。

## 专题页规则

### 视觉

- **每个专题页按该模型官网的风格单独设计，不套固定模板。** 配色、字体气质、版块节奏都参考官网。样式写在 `assets/models/<slug>.css`，类名用模型专属前缀（Suno 用 `s-`），避免和其他专题冲突。
- 不使用专辑封面、产品截图、插画等素材，用 CSS 渐变、SVG、波形等自己画。
- **模型 logo 一律用 lobe-icons，不要自己画**（MIT 协议，https://github.com/lobehub/lobe-icons ，图标检索 https://lobehub.com/zh/icons ）。
  - 下载固定版本的 SVG 到 `assets/icons/<id>.svg`（地址 `https://registry.npmmirror.com/@lobehub/icons-static-svg/<版本>/files/icons/<id>.svg`，版本号写在 `scripts/icons.py` 的 `VERSION`）。有 `-color` 彩色版就用彩色版（如 `claude-color`），没有就用单色版并在 SVG 上写 `fill`（如 `suno` 在深色页用白色）。
  - 新模型：把 id 加进 `scripts/icons.py` 的 `ICONS`，运行 `python scripts/icons.py --fetch`，再在脚本里加对应页面的替换规则。脚本把 path 内联进页面（首屏、结尾、专题首页卡片），重复运行结果不变。
  - 分享图用同一份 SVG（`scripts/og_claude.py` 读 `assets/icons/claude-color.svg`）。
  - 页脚商标声明照常保留。
- 专题首页（`/zh/models/` 等 6 种语言）统一用 `hub.css`，沿用站点首页的暖黑配色和 logo 顶栏，不按模型变。
- **站点视觉（2026-11-23 起）：** 站点首页、专题首页、隐私政策、服务条款、404 统一为暖黑底、配色取自品牌 logo（`assets/home/logo.webp`）：底 `#0f0b0a`，奶油文字 `#f6ede3`，主强调珊瑚 `#f68766`，辅助青绿 `#47b4b6`、黄 `#ffd166`，珊瑚按钮上的字 `#2a0d08`。变量定义在 `assets/home/home.css` 的 `:root`，`hub.css`、`legal.css` 各自复制了一份，改色要三处一起改。以前的暖白加珊瑚风格不再使用。顶栏品牌一律用 logo 图片（`/assets/home/logo.webp?v=…`，显示高度 42px），不要再用文字。各模型专题页仍按各自模型官网的风格设计，不受这条限制。
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
- 改了全站文案（如模型数、注册链接）要同时改 `scripts/home_copy/<lang>.json`（再运行 `python scripts/home_page.py`，不要手改 6 个 `index.html`）、`privacy.html`、`terms.html`（改了要同步 `scripts/legal_copy/`，见上）、`README.md`、`README.en.md` 和所有专题页。
