export const meta = {
  name: 'legal-i18n',
  description: '隐私政策和服务协议 5 种语言（en ja ko es de）：译者并行翻译 scripts/legal_copy/src.json，译完各配一个独立复核人，都用 check_legal_copy.py 自检',
  phases: [{ title: 'Translate', detail: '5 个译者并行' }, { title: 'Review', detail: '5 个独立复核人并行' }],
}

const BRIEF = 'scripts/i18n/briefs/legal.md'
const LANGS = [
  { code: 'en', name: '英语', note: '正式的法律文本英语（plain legal English），避免过时的法律套话。' },
  { code: 'ja', name: '日语', note: '法的文書の敬体（です・ます）、「お客様」。「および」「または」の表記は全文統一。' },
  { code: 'ko', name: '韩语', note: '합니다体，법적 문서 문체，「귀하」或「이용자」全文统一。' },
  { code: 'es', name: '西班牙语（通用，不限地区）', note: '用 usted，正式法律文本语体，不带地区特征。' },
  { code: 'de', name: '德语（通用）', note: '用 Sie，标准德语法律文本语体，复合词连写。' },
]
const RESULT = {
  type: 'object',
  properties: { lang: { type: 'string' }, errors: { type: 'number' }, warnings: { type: 'number' }, changed: { type: 'number' }, notes: { type: 'array', items: { type: 'string' } } },
  required: ['lang', 'errors'],
}

const tPrompt = (L) => `你是一名${L.name}法律文本译者。把 scripts/legal_copy/src.json 里的《隐私政策》（privacy，84 个单元）和《服务协议》（terms，96 个单元）从中文翻译成${L.name}，写入 scripts/legal_copy/${L.code}.json。

先完整读 ${BRIEF}（法律文本翻译原则、输出结构、固定译法表、必须原样保留的东西）。${L.note}

同一语言里站点其他页面已有的译文，可以对照用词（只读）：scripts/home_copy/${L.code}.json（若存在，最后的 final、foot 两块要与 CTA 区块和页脚链接的译法一致）、${L.code === 'en' ? 'en/models/gpt.html' : L.code + '/models/gpt.html'} 的页脚和导航。

输入：src.json，格式 {"privacy": [{"id":"u0","kind":"unit","text":"…"}, …], "terms": […]}。输出 ${L.code}.json，格式 {"privacy": {"u0": "译文", …}, "terms": {…}}，每个 id 都要有，不多不少。kind 为 attr:meta:description 的是 meta 描述，attr:aria-label / attr:alt 是无障碍文字，其余是页面正文单元。

你的流程：
1. 用 Write 工具直接写出完整 JSON（不要写辅助脚本批量生成译文；JSON 里的双引号要转义，译文里避免出现英文双引号，需要引号时用各语言的引号：英语 “ ”，日语 「 」，韩语 “ ”，西语 « »，德语 „ “）。分两次写也可以（先写 privacy，再追加 terms），但最终文件必须是完整的一个 JSON。
2. 运行 python scripts/i18n/check_legal_copy.py ${L.code}，ERROR 必须改到 0，WARN 逐条看一遍，该改的改。
3. 自己通读一遍：忠实、不增不减、权利义务和限定词的力度与中文一致；目录里的每个标题和正文里对应的标题一模一样；「服务协议」「服务条款」统一成同一个词。

范围：只写 scripts/legal_copy/${L.code}.json。不要改其他文件，不要运行 scripts/legal_pages.py，不要 git commit，不要自己再开其他代理。
最后一步调用 StructuredOutput：lang、errors（最终 ERROR 数）、warnings、changed（0）、notes（原文里你认为有问题、含糊或需要人判断的地方，最多 5 条，不要自己改原文的意思）。`

const rPrompt = (L) => `你是${L.name}法律文本的独立复核人，没有参与翻译。目标：把 scripts/legal_copy/${L.code}.json 复核到可以直接上线。

先读 ${BRIEF}。对照 scripts/legal_copy/src.json（中文原文）逐条检查。直接修改 ${L.code}.json 里确有问题的值（不要改键，不要增删单元），其余不动。

五个角度逐项检查：
- fact：权利义务、范围、例外、限定词（「除非法律法规要求」「可能」「不超过」「包括但不限于」「有权」「不承担责任」）的力度和中文一致，没有加重也没有削弱；数字（30 天、1.1、2026 年 1 月 1 日）、列表项的条数和顺序与中文一致；没有补充中文里没有的条款、承诺或例子。
- context：正式、中性的${L.name}法律文本语体，不是翻译腔，也不是营销腔；人称（您 → ${L.code === 'en' ? 'you' : L.code === 'ja' ? 'お客様' : L.code === 'ko' ? '귀하/이용자，全文统一' : L.code === 'es' ? 'usted' : 'Sie'}）和「本平台 / 我们」全文统一。
- term：与简报固定译法表一致；同一概念全文只用一个词（账号/账户、个人信息、第三方服务提供商、基础设施服务商、持久化存储、跨境传输、不可抗力、责任限制等）；「服务协议 / 服务条款」统一成 Terms of Service 这一个词。
- structure：目录条目和正文标题一模一样；小节编号全部是阿拉伯数字加点；HTML 标签、实体和链接文字保留。
- residue：没有漏译整句、没有残留汉字（日语除外）和中文标点；没有英文以外语言的混入。

改完运行 python scripts/i18n/check_legal_copy.py ${L.code}，ERROR 必须为 0。范围：只改 scripts/legal_copy/${L.code}.json。不要改其他文件，不要运行 scripts/legal_pages.py，不要 git commit，不要自己再开其他代理。
最后一步调用 StructuredOutput：lang、errors、warnings、changed（你改了多少个值）、notes（改动要点和真正需要人判断的地方，最多 6 条）。`

phase('Translate')
const t = await parallel(LANGS.map(L => () => agent(tPrompt(L), { label: `translate:${L.code}`, phase: 'Translate', schema: RESULT })))
phase('Review')
const ready = LANGS.filter((L, i) => t[i])
const r = await parallel(ready.map(L => () => agent(rPrompt(L), { label: `review:${L.code}`, phase: 'Review', schema: RESULT })))
return { translate: t.filter(Boolean), review: r.filter(Boolean), missingTranslators: LANGS.filter((L, i) => !t[i]).map(L => L.code) }
