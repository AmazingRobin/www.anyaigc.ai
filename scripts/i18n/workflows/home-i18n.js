export const meta = {
  name: 'home-i18n',
  description: '根首页 4 种语言（ja ko es de）：译者并行翻译 scripts/home_copy/en.json，译完各配一个独立复核人，都用 check_home_copy.py 自检',
  phases: [{ title: 'Translate', detail: '4 个译者并行' }, { title: 'Review', detail: '4 个独立复核人并行' }],
}

const BRIEF = 'scripts/i18n/briefs/home.md'
const LANGS = [
  { code: 'ja', name: '日语', tone: '敬体（です・ます）；APIキー不带空格；「300+」写「300以上」；原文没有 about / ~ 的地方不要加「約」。' },
  { code: 'ko', name: '韩语', tone: '합니다体技术文档语气；敬体统一「~하세요」，疑问句统一「~입니까/합니까」；「300+」写「300개 이상」；WeChat Pay、Alipay 写英文原名。' },
  { code: 'es', name: '西班牙语（通用，不限地区）', tone: '专业、统一用 tú 或无人称；「300+」写「más de 300」；Business 译 Negocios，Enterprise 译 Empresas；请求用 petición；vídeo 带重音。' },
  { code: 'de', name: '德语（通用）', tone: '统一用 Sie；复合词连写；「300+」写「über 300」；Anfrage 全文统一；按钮和短标签不超过 28 个字符。' },
]
const RESULT = {
  type: 'object',
  properties: { lang: { type: 'string' }, errors: { type: 'number' }, warnings: { type: 'number' }, changed: { type: 'number' }, notes: { type: 'array', items: { type: 'string' } } },
  required: ['lang', 'errors'],
}

const tPrompt = (L) => `你是一名${L.name}技术文档本地化译者。把英文首页文案 scripts/home_copy/en.json 翻译成${L.name}，写入 scripts/home_copy/${L.code}.json。

先完整读 ${BRIEF}（键结构规则、不翻译的键、固定译法表、口径、风格）。再读同一语言里已经复核过的专题首页译文，对照用词和语气（只读）：drafts/i18n/hub/out/${L.code}-all.json 里前 80 条，以及 ${L.code}/models/gpt.html 的可见文字（导航、按钮、企业接入、信任、FAQ 那几块，用 grep 或 Python 去掉标签后读）。这个首页的词（Get an API Key、Model Guides、Self-service invoices 等）必须和它们一致。

输出文件结构与 en.json 完全相同（同样的键、同样的数组长度），只把字符串的值译成${L.name}。lang / html_lang / og_locale / native 四个键按简报表填。${L.tone}

你的流程：
1. 用 Write 工具直接写出完整 JSON 文件（不要写辅助脚本批量生成译文；JSON 里的双引号要转义成 \\"，HTML 标签里的属性引号也一样；译文里不要出现未转义的英文引号）。
2. 运行 python scripts/i18n/check_home_copy.py ${L.code}，ERROR 必须改到 0，WARN 逐条看一遍，该改的改。
3. 自己通读一遍：像当地开发者写的文档，不是逐词直译；意思必须与英文一致；不添加原文没有的承诺、数字、功能；不出现增值税、对公转账、合同、国内直连、SLA。

范围：只写 scripts/home_copy/${L.code}.json。不要改其他文件，不要运行 scripts/home_page.py，不要 git commit，不要自己再开其他代理。
最后一步调用 StructuredOutput：lang、errors（最终 ERROR 数）、warnings、changed（0）、notes（真正需要人判断的地方，最多 4 条）。`

const rPrompt = (L) => `你是${L.name}的独立复核人，没有参与翻译。目标：把 scripts/home_copy/${L.code}.json 复核到可以直接上线。

先读 ${BRIEF}。对照 scripts/home_copy/en.json（源文）逐条检查，同一语言里已复核过的译文（只读）在 drafts/i18n/hub/out/${L.code}-all.json 和 ${L.code}/models/gpt.html，用词和语气要与它们一致。直接修改 scripts/home_copy/${L.code}.json 里确有问题的值（不要改键、不要改数组长度和顺序），其余不动。

五个角度逐项检查：
- fact：数字（300+、$1、500 万 / 5M tokens、7×24）、模型和工具名、链接占位符、能力描述与英文一致；没有新增或漏掉的事实、承诺；没有 SLA、国内直连、增值税、对公转账、合同。发票只写“在控制台自助开具”。
- context：像${L.name}母语者写的开发者文档，不是翻译腔；语气和敬体全文一致；标题和描述里有当地开发者会搜的词；hero.h1a + h1b 连起来读是一句通顺的话（h1b 是渐变高亮的那半句）。
- term：与简报固定译法表一致；同一概念全文只用一个词（例如 API Key、Base URL、model ID、tokens、console）。
- residue：没有漏译整句、没有英文残留（品牌名、技术词除外）、没有其他语言混入。
- length：title、desc 长度合规；nav 五项、login、cta_key 够短（手机顶栏很窄）；按钮文字不过长；stats 的说明不超过一行半。

改完运行 python scripts/i18n/check_home_copy.py ${L.code}，ERROR 必须为 0。范围：只改 scripts/home_copy/${L.code}.json。不要改其他文件，不要运行 scripts/home_page.py，不要 git commit，不要自己再开其他代理。
最后一步调用 StructuredOutput：lang、errors（最终 ERROR 数）、warnings、changed（你改了多少个值）、notes（改动要点和真正需要人判断的地方，最多 6 条）。`

phase('Translate')
const t = await parallel(LANGS.map(L => () => agent(tPrompt(L), { label: `translate:${L.code}`, phase: 'Translate', schema: RESULT })))
phase('Review')
const ready = LANGS.filter((L, i) => t[i])
const r = await parallel(ready.map(L => () => agent(rPrompt(L), { label: `review:${L.code}`, phase: 'Review', schema: RESULT })))
return { translate: t.filter(Boolean), review: r.filter(Boolean), missingTranslators: LANGS.filter((L, i) => !t[i]).map(L => L.code) }
