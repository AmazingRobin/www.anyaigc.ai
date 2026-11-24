# 多语言页面（ja / ko / es / de）开发流程

2026-11-17 起为站点新增日语 `/ja/`、韩语 `/ko/`、西班牙语 `/es/`、德语 `/de/`。范围：专题页、专题首页、站点首页、隐私政策、服务条款（404 页不做多语言）。
西语、德语用通用版本，不分地区。质量保证只用 AI 交叉检查，没有母语审校。

**新增一个模型专题页时怎么做，见 `AGENTS.md`「新语言（ja/ko/es/de）」一节（有逐步清单）。本文件是各个脚本的细节。**

## 原则

1. **源文是英文页，不是中文页。** 英文页已经是本地化改写。
2. **价格、模型 ID、代码、URL、数字原样保留。** 翻译只动文字。价格和小数一律用小数点（0.0596），德语、西语也不用逗号。
3. **非中文页面（含英文页）的企业口径**：
   - 发票写成"在控制台自助开具，按实际充值金额"，不写增值税、专票、中国发票流程。
   - 支付方式保留微信支付、支付宝、USDT、信用卡，去掉"对公转账"。
   - 删掉「对公转账」「签订合同」两张卡片和对应 FAQ；保留"专属客服与技术对接"。
   - 不写"能否从中国大陆调用"这类卖点（见记忆 `en-no-china-access-claim`）。
   - 不写 SLA、可用率、企业专属分组或线路（CLAUDE.md）。
4. **不要为了凑长度而扩写。** 译文要像当地开发者文档，不是英文的逐词对应。
5. **翻译者和复核者不能是同一个代理。** 复核按 id 段并行，只写补丁文件，不碰总文件。
6. **不自动 commit。**

## 文件

| 文件 | 作用 |
| :--- | :--- |
| `langs.py` | 语言表（目录、hreflang、og:locale、自称） |
| `htmlseg.py` | 把页面切成翻译单元并精确回填；代码、SVG、模型 ID、语言菜单不进翻译 |
| `overseas.py` | 把英文页改成海外口径（卡片、FAQ、描述、支付行），自带残留检查；**运行后自动把前缀登记进 `overseas_done.json`**（`check_topics.py` 只对登记过的前缀检查英文页） |
| `china_faq.py` / `china_body.py` | 删掉英文页里「能否从中国大陆调用」的 FAQ 和正文里的大陆直连说法 |
| `batch.py` | 一个系列的翻译批次：`prepare` 合并去重分块、`tm-fill` 用记忆库、`tm-chunks` 重新分块、`validate` 校验、`render` 渲染、`tm-save` 存记忆库 |
| `merge_tm.py` | 合并翻译记忆库：`merge_tm.py <目标> --all` 合并所有已有系列 |
| `consolidate.py` / `merge_patches.py` / `check_patch.py` | 把分散的译文合成 `<lang>-all.json`；合并复核补丁；校验一个复核段 |
| `resync.py` | 英文源页改动后，把已复核的译文按"角色+原文"重新映射到新的 union，缺的写成 `todo-resync-<lang>.json` |
| `build.py` | 单页回填；改路径、6 语言 hreflang、og、语言菜单；首页链接和隐私/条款链接改成各语言自己的页面 |
| `register.py` | 写 sitemap；给已有 zh/en 页补 hreflang 和语言菜单 |
| `relink_home.py` | 把 en/ja/ko/es/de 页里指向 `/`、`/privacy`、`/terms` 的链接改成各语言自己的；面包屑 item 同理 |
| `org_logo.py` | 把专题页 JSON-LD 的 `Organization.logo` 换成新 logo（`/assets/home/logo-512.png`） |
| `decimal_point.py` | 把 es/de 页里的小数逗号改回小数点（html / series / tm 三种模式） |
| `check_home_copy.py` / `check_legal_copy.py` | 站点首页文案、法律页译文的自检 |
| `briefs/<系列>.md` | 该系列的术语表和各语言风格，翻译时整份附上 |
| `workflows/translate-group.js` | 翻译工作流：4 种语言 × N 块，分波并行 |
| `workflows/review-segmented.js` | 复核工作流：按 id 段并行，只写 `<lang>-rev-<seg>.json` 补丁；`args.only=["ja-s0",…]` 可只补跑指定段 |
| `workflows/home-i18n.js`、`legal-i18n.js` | 站点首页、法律页的翻译加复核工作流 |
| `../og_<系列>.py --langs=ja,ko,es,de` | 新语言分享图；`--langs=en` 只重出英文图；每个系列的脚本各自有新语言文案词表 |
| `drafts/i18n/<系列>/` | 翻译稿、翻译记忆库。**`drafts/` 在 .gitignore 里，不进仓库**，换机器就没有了，记忆库丢了只是要重新翻译 |

## 单个系列的流程（S = 该系列所有 slug，P = slug 前缀）

```bash
export PYTHONIOENCODING=utf-8
python scripts/check_topics.py                              # 0 起点必须 0 错误
python scripts/i18n/overseas.py P                           # 1 英文页改成海外口径，自动登记前缀
python scripts/i18n/china_faq.py P && python scripts/i18n/china_body.py P
mkdir -p drafts/i18n/<系列>
python scripts/i18n/merge_tm.py <系列> --all                # 2 合并所有已有的翻译记忆库
python scripts/i18n/batch.py prepare <系列> $S              # 3 合并去重，写 union.json
for l in ja ko es de; do python scripts/i18n/batch.py tm-fill <系列> $l; done   # 4 记忆库命中的直接用，未命中的才翻译
python scripts/i18n/batch.py tm-chunks <系列> 11000         # 5 只把未命中的分块；再把 chunks/*.json 复制成 todo/<lang>-<NN>.json
#   6 翻译：workflows/translate-group.js（args：series chunks wave brief desc refs）
#   7 consolidate → 复核：workflows/review-segmented.js（args：series total segs brief desc refs extra）→ check_patch → merge_patches
python scripts/i18n/batch.py validate <系列> <lang>         # 8 校验
python scripts/i18n/batch.py render <系列> <lang> $S        # 9 渲染成 <lang>/models/<slug>.html
python scripts/i18n/register.py $S                          # 10 sitemap + 给 zh/en 页补 hreflang 和语言菜单
python scripts/i18n/decimal_point.py html                   # 11 es/de 的小数逗号改回小数点（只改译文新产生的）
python scripts/og_<系列>.py --langs=ja,ko,es,de             # 12 分享图（先给脚本加四种语言文案，es/de 价格用小数点）
python scripts/i18n/relink_home.py && python scripts/i18n/org_logo.py   # 13 首页、法律页链接和 logo
python scripts/related_models.py                            # 14 同类模型版块
python scripts/check_topics.py                              # 15 必须 0 错误
#   16 版面抽样：日语和德语各一页，390px 量 scrollWidth（别大量截图）；scripts/i18n/mobile_probe.py、width_scan.py
```

### 翻译记忆库

记忆库键是 `role + 0x1f + 原文`。`merge_tm.py --all` 会把所有系列的记忆库合进新系列；英文源页改动后同样用 `prepare` → `tm-fill`，只补译变化的句子；复核完成后用 `batch.py tm-save <系列> <lang>` 存回。
`prepare` 之后如果英文页又改了，先 `resync.py <系列>`，再补译 `todo-resync-<lang>.json` 里缺的条目。

### 翻译源
所有系列的翻译源都是 `build.source(slug)`：英文页去掉"中国大陆可访问"的卖点（FAQ 整条删、句子里的 "direct access from mainland China" 删）。
`extract`、`prepare`、`build` 必须用同一个源，否则单元编号对不上。
`build.source()` 还会把英文页里指向 `/en/`、`/en/privacy`、`/en/terms` 的链接还原成 `/`、`/privacy`、`/terms`（`relink_home.py` 改过英文页之后，各系列保存的原文仍是旧写法）；渲染时 `localize()` 再把它们转成各语言自己的首页和法律页，并把指向 `/en/models/…` 的内部链接转成各语言自己的页面。**不要改动这两处，否则已有系列的译文会对不上、被当成要重新翻译。**

### 专题首页（6 种语言）
`index` 当作一个 slug 走同样的流程（prepare / merge_tm / tm-fill / 翻译 / 复核 / render index）。新增模型后，4 种新语言的专题首页也要补卡片：对 hub 系列重新 `prepare`，`resync` 之后补译缺口，再 `render hub <lang> index`。

### 站点首页（`/`、`/en/` … 6 种语言）
由 `scripts/home_page.py` 生成，文案在 `scripts/home_copy/<lang>.json`（`en.json` 是源文）。改文案改 JSON，运行 `python scripts/home_page.py`；`python scripts/i18n/check_home_copy.py <lang>` 自检。不要手改 `index.html`。

### 隐私政策、服务条款（6 种语言）
中文原文是根目录 `privacy.html`、`terms.html`；其他语言由 `scripts/legal_pages.py` 生成到 `/<lang>/privacy`、`/<lang>/terms`，译文在 `scripts/legal_copy/<lang>.json`。改了中文原文：先 `python scripts/legal_pages.py extract`，重新翻译变化的单元，`python scripts/i18n/check_legal_copy.py <lang>` 自检，再 `python scripts/legal_pages.py build`。法律文本译文只是对照译本，以中文为准，上线前建议让有资质的人审阅。

### 分享图和导航
- `python scripts/og_<系列>.py --langs=ja,ko,es,de`：每个系列的 og 脚本各自加新语言文案（见 `og_claude.py`）。Chrome 偶发静默失败、旧图被原样写回，出图后要核对每张的修改时间。
- `python scripts/i18n/nav_probe.py <slug> es,de,ja,ko 390,1100,1200,1440`：量各宽度下导航是否溢出；西德语导航文字长，必要时在 `build.py` 的 `NAV_SHORT` 里加短写法。

## 交叉检查的角度（翻译者与检查者不能是同一个代理）

- **事实**：数字、价格、模型 ID、折扣百分比、参数、接口路径与英文逐项一致；没有新增或漏掉的事实、承诺（没有 SLA、中国大陆访问、海外信用卡、增值税、对公转账、合同）。
- **语境**：像当地开发者写的文档，不是翻译腔；语气、敬体、称呼全文一致；标题和描述里有当地开发者会搜的词。
- **术语**：与简报术语表一致；同一概念全文只用一个词，并与已复核系列一致。
- **残留**：没有漏译整句、没有汉字（日语除外）、没有其他语言混入。
- **结构**：标签、占位符、`<code>` 与原文一致。

## 已知的坑

- 工作流里并发跑太多代理会限流（429）；一次 12 到 16 个比较稳。
- 代理偶尔不调用 StructuredOutput 就结束，补丁文件没写出，要按段重跑（`review-segmented.js` 的 `args.only`）。
- 合并补丁前要等补丁文件 90 到 120 秒没有变化，并且收到工作流完成通知。
- 翻译代理会在 `scripts/` 和 `drafts/` 下留 `_build*.py` 之类的临时文件，收尾时挪到 `drafts/i18n/_scratch/`。
- 在 bash 里用 heredoc 写含反斜杠的 Python 会被转义破坏（例如 `\b` 变成退格符）；复杂内容用 Write 或 Edit 工具。
- 用户说"暂停"之后，不要自己续跑工作流，等用户说继续。
