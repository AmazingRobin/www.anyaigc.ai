# 多语言专题页（ja / ko / es / de）开发流程

2026-11-17 确认：给 `/models/` 下的专题页新增日语 `/ja/`、韩语 `/ko/`、西班牙语 `/es/`、德语 `/de/`。
范围只含专题页和专题首页；站点首页、隐私政策、服务条款不做。西语、德语用通用版本，不分地区。
质量保证只用 AI 交叉检查，没有母语审校。已用 DeepSeek 系列（4 页 × 4 语言）跑通试点。

## 原则

1. **源文是英文页，不是中文页。** 英文页已经是本地化改写。
2. **一个系列一个系列做。** 每个系列做完、自检 0 错误后给用户确认，再做下一个。不自动 commit。
3. **价格、模型 ID、代码、URL、数字原样保留。** 翻译只动文字。
4. **非中文页面（含现有英文页）的企业口径**：
   - 发票写成"在控制台自助开具，按实际充值金额"，不写增值税、专票、中国发票流程。
   - 支付方式保留微信支付、支付宝、USDT、信用卡，去掉"对公转账"。
   - 删掉「对公转账」「签订合同」两张卡片和对应 FAQ；保留"专属客服与技术对接"。
   - 不写"能否从中国大陆调用"这类卖点（见记忆 `en-no-china-access-claim`），新语言页构建时自动删掉该 FAQ。
   - 不写 SLA、可用率、企业专属分组或线路（CLAUDE.md）。
5. **不要为了凑长度而扩写。** 译文要像当地开发者文档，不是英文的逐词对应。

## 文件

| 文件 | 作用 |
| :--- | :--- |
| `langs.py` | 语言表（目录、hreflang、og:locale、自称） |
| `htmlseg.py` | 把页面切成翻译单元并精确回填；代码、SVG、模型 ID、语言菜单不进翻译 |
| `overseas.py` | 把英文页改成海外口径（卡片、FAQ、描述、支付行），自带残留检查 |
| `batch.py` | 一个系列的翻译批次：合并去重、分块、校验、翻译记忆库、渲染 |
| `build.py` | 单页回填；改路径、6 语言 hreflang、og、语言菜单；FAQ 与 JSON-LD 同步 |
| `register.py` | 写 sitemap；给已有 zh/en 页补 hreflang 和语言菜单（重复运行不变） |
| `og_margin.py` | 检查分享图标签行右边距 |
| `briefs/<系列>.md` | 该系列的术语表和各语言风格，翻译时整份附上 |
| `../og_<系列>.py --langs=ja,ko,es,de` | 生成新语言分享图（每个系列的脚本要各自加语言文案） |
| `drafts/i18n/<系列>/` | 翻译稿、翻译记忆库（`drafts/` 在 .gitignore，不进仓库） |

## 单个系列的流程（以 DeepSeek 为例，S = 该系列所有 slug）

```bash
export PYTHONIOENCODING=utf-8
python scripts/check_topics.py                         # 0 · 先确认起点是 0 错误
python scripts/i18n/overseas.py <系列前缀>              # 1 · 英文页改成海外口径（并把前缀登记进 overseas_done.json）
python scripts/i18n/batch.py prepare <系列> $S          # 2 · 合并去重，写 union.json 和 chunks/
#   3 · 翻译：每个 chunk × 4 语言一个代理，写 out/<lang>-<NN>.json（Workflow 并行），随后每种语言一个独立复核代理
python scripts/i18n/batch.py validate <系列> <lang>     # 4 · 脚本校验：id、标签、价格小数、实体、<code>、字符集、标题/描述宽度
python scripts/i18n/batch.py render <系列> <lang> $S    # 5 · 合并并回填成 <lang>/models/<slug>.html
python scripts/i18n/register.py $S                     # 6 · sitemap + 给 zh/en 页补 hreflang 和语言菜单
python scripts/og_<系列>.py --langs=ja,ko,es,de         # 7 · 分享图（先给脚本加四种语言文案）
python scripts/i18n/og_margin.py <系列前缀>             # 8 · 右边距检查
python scripts/check_topics.py                         # 9 · 自检，必须 0 错误
#   10 · 390px 宽度抽样：日语和德语各一页，量 scrollWidth（别大量截图）
```

### 翻译记忆库（后面的系列先复用前面的译文）

```bash
cp drafts/i18n/<已完成系列>/tm-<lang>.json drafts/i18n/<新系列>/tm-<lang>.json   # 每种语言各一份
python scripts/i18n/batch.py tm-fill <系列> <lang>     # 命中的写 out/<lang>-tm.json，未命中的写 delta-<lang>.json
python scripts/i18n/batch.py tm-chunks <系列> 18000    # 只把未命中的重新分块，翻译块更大、代理更少
#   …翻译、复核、validate、render…
python scripts/i18n/batch.py tm-save <系列> <lang>     # 复核完成后把译文存回 tm-<lang>.json
```

记忆库键是 `role + 0x1f + 原文`。Claude 从 DeepSeek 复用了 102/1172 条（只有导航、页脚、企业接入这类公共文案）。
英文源页改动后，同样用 `prepare` → `tm-fill`，只补译变化的句子。

### 翻译源
所有系列的翻译源都是 `build.source(slug)`：英文页去掉"中国大陆可访问"的卖点（FAQ 整条删、句子里的 "direct access from mainland China" 删）。
`extract`、`prepare`、`build` 必须用同一个源，否则单元编号对不上。

### 分享图和导航
- `python scripts/og_<系列>.py --langs=ja,ko,es,de`：每个系列的 og 脚本各自加 SUBS_I18N / TAGS_I18N（见 `og_claude.py`）。
- `python scripts/i18n/nav_probe.py <slug> es,de,ja,ko 390,1100,1200,1440`：量各宽度下导航是否溢出；西德语导航文字长，必要时在 `build.py` 的 `NAV_SHORT` 里加短写法。

## 交叉检查的角度（翻译者与检查者不能是同一个代理）

- **事实**：数字、价格、模型 ID、折扣百分比与英文逐项一致；没有新增原文没有的承诺或数字。
- **语境**：像当地开发者文档；敬体和称呼一致；标题里有当地人会搜的词。
- **术语**：与简报一致；同一概念全文只用一个词，跨文件对照。
- **残留**：没有漏译、没有中文、没有机翻痕迹。
- **结构**：标签、占位符、`<code>` 与原文一致（`build.py` 和 `batch.py validate` 都会硬性拦截）。

## 已知坑

- 简报文件不要叫 `claude.md`、`agents.md`：Windows 文件名不分大小写，Claude Code 会把它当项目指令文件自动加载。Claude 系列的简报叫 `briefs/claude-series.md`。
- 在 Python 字符串里写 `\b` 会被写成退格字符（0x08）。改完脚本要查：
  `python -c "b=open(p,'rb').read(); print(b.count(bytes([8])))"`，非 0 就把 0x08 换成 `bytes([92,98])`。
- **工作流跑着的时候，不要对同一个系列运行 `tm-fill`、`tm-chunks`、`prepare`、`render`。** 2026-11-18 试渲染时 `tm-fill` 把 `out/<lang>-*.json` 全部删了，翻译者和复核代理的成果一起丢失。
  现在 `tm-fill` 不再删文件，但 `prepare` / `tm-chunks` 仍会重写 `union.json` 和 `chunks/`，编号会错开。
  需要预览时，等工作流结束，或把 `drafts/i18n/<系列>/` 整个复制一份再试。
- 译文丢了怎么办：工作流代理是用脚本写译文的，脚本留在系统 Temp 目录里，对话记录在 `~/.claude/projects/.../subagents/workflows/<run>/agent-*.jsonl`。
  `drafts/i18n/_recover.py plan|replay <label>` 能按记录重放代理的命令还原译文（Claude 系列当时还原了 24/28 块，其余用 `remap.py` 按原文迁移 + 补译）。
- 翻译源变了（改了改写规则、修了英文错字）导致 `union.json` 编号错开：用 `remap.py` 按「角色 + 原文」把旧译文迁移到新编号，只重译原文变了的条目。
- 补译零散缺失的句子：`todo/<lang>-<n>.json` → 译者写 `out/<lang>-todo-<n>.json` → `check_todo.py` 自检 → `consolidate.py` 合并成 `out/<lang>-all.json`（之后 validate / render 都只读它）。
- **英文页的「能否从中国大陆调用」FAQ** 用 `python scripts/i18n/china_faq.py` 处理（2026-11-18 用户确认删除）：纯问题整条删，复合问题（并发/xAI 账号/取 key）只去掉中国相关部分，可见 FAQ 与 JSON-LD 同步。重复运行不变；系列重新生成英文页后要再跑一次。正文里的「mainland China」卖点（卡片标题、介绍句）用 `python scripts/i18n/china_body.py` 处理（2026-11-18 用户确认删除）：卡片换成不带中国说法的标题并保留其它事实，卡片数量不变，meta keywords 里的 "OpenAI/Gemini API China" 一并删掉；句子用 `overseas.CHINA_RULES` 删掉那一小段（新语言页翻译源用同一组规则）。重复运行不变，系列重新生成英文页后要再跑一次。
- 英文页数据里的坏日期（`scripts/seo_specs_data.json` 的 `facts_en` 串字）已修；改完要跑 `python scripts/seo_unique_specs.py` 写回页面。
- 分享图标签行：西语、德语文案长，标签必须 `white-space:nowrap` 并缩小字号；改文案后跑 `og_margin.py`。
- `scripts/payments.py` 对 kling、seedance 总览这类 JSON-LD 压成一行的页面会报错，
  它已改成不写对公转账，但不要对全站直接重跑；对已转换系列用 `overseas.py` 即可。
- 新语言的专题首页最后统一做；首页上线前，页面里指向 `/<lang>/models/` 的链接先退回英文页，
  系列页上线后用 `python scripts/i18n/build.py relink <lang> <slug>...` 重新指向。

## 待办

- [ ] 新语言专题首页（`hub.css` 的 `af-*` 风格，四种语言）和 sitemap 里首页条目
- [ ] 其余系列的 `og_*.py` 加四种语言
- [ ] 英文源页两处 FAQ 不一致（gemini-4-argon、gemini-4-hydrogen 的 "Contact" 与 "Talk to"），轮到 Gemini 时先修
- [ ] Kling / Seedance 总览页和 doubao-seedance-* 结构特殊（FAQ 没有 `<h3>`、JSON-LD 压成一行），单独验证

## 系列顺序

| 批次 | 内容 | 状态 |
| :--- | :--- | :--- |
| 试点 | DeepSeek（4 页） | 完成，用户已确认三项译法 |
| 第 1 批 | Claude（12） | 完成 |
| 第 1 批 | Gemini（6）、Suno（1）、Midjourney（1） | 完成，等用户确认 |
| 第 2 批 | GPT（17）、Grok（17） | |
| 第 3 批 | Doubao、Seedream、Seedance、Kimi、GLM、MiMo、MiniMax | |
| 第 4 批 | Kling、Vidu、Viduq、Wan、HappyHorse、Muse、Hailuo | |
| 第 5 批 | Qwen（30）、Llama、Eleven、Speech、Jev、Spark、Hy 等 | |
| 收尾 | 专题首页、sitemap lastmod、全站自检 | |
