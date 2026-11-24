export const meta = {
  name: 'i18n-translate-group',
  description: '某一批的某一组：4 种语言 × N 块翻译，每种语言按波发起（波内并行），失败重试一次；只翻译，复核另开工作流',
  phases: [{ title: 'Translate', detail: '4 种语言同时跑，每种语言按波翻译' }],
}

// args: { series, chunks, wave, brief, desc, refs: [series...] }
const SERIES = args.series
const N = args.chunks
const WAVE = args.wave
const BRIEF = args.brief
const DESC = args.desc
const REFS = args.refs
const DIR = `drafts/i18n/${SERIES}`
const CHUNKS = Array.from({ length: N }, (_, i) => String(i).padStart(2, '0'))
const WAVES = []
for (let i = 0; i < CHUNKS.length; i += WAVE) WAVES.push(CHUNKS.slice(i, i + WAVE))
const LANGS = [
  { code: 'ja', name: '日语', tone: '敬体（です・ます）。APIキー不带空格；「1M context」写「コンテキスト長1M」；原文没有 about / ~ 的地方不要加「約」。' },
  { code: 'ko', name: '韩语', tone: '합니다体技术文档语气；敬体统一「~하세요」，疑问句统一「~입니까/합니까」；list price 译「공식 정가」；「300+」译「300개 이상」；带波浪线的「~12%」用「약」；微信支付、支付宝写英文原名 WeChat Pay、Alipay。' },
  { code: 'es', name: '西班牙语（通用）', tone: '专业、无人称或统一 tú。小数点用逗号。Business 译 Negocios，Enterprise 译 Empresas；请求统一用 petición；「~12%」译「aproximadamente el 12 %」；「300+ modelos」写「más de 300 modelos」；vídeo 带重音。' },
  { code: 'de', name: '德语（通用）', tone: '统一用 Sie；复合词连写；小数点用逗号；「~12%」译「rund 12 %」；Anfrage 全文统一；按钮和短标签不超过 28 个字符。' },
]

const SUMMARY = {
  type: 'object',
  properties: {
    lang: { type: 'string' }, chunk: { type: 'string' }, items: { type: 'number' },
    validateErrors: { type: 'number' }, notes: { type: 'array', items: { type: 'string' } },
  },
  required: ['lang', 'items', 'validateErrors'],
}

const refList = (L) => REFS.map(r => `drafts/i18n/${r}/out/${L.code}-all.json`).join('、')

const prompt = (L, c) => `你是一名${L.name}技术文档本地化译者。把 ${DIR}/todo/${L.code}-${c}.json 里的英文翻译成${L.name}，写入 ${DIR}/out/${L.code}-todo-${c}.json。

先完整读：${BRIEF}（术语表、必须原样保留的东西、已确认的译法、风格）。再读同一语言里已经复核过的译文，对照用词（只读，不要修改）：${refList(L)} 各取前 50 条。这批是${DESC}，读者是${L.name}使用者里的开发者，用词和语气必须与前几个系列已有译文一致。

输入是 JSON 数组，每项 {id, text, role, pages}。输出同样是 JSON 数组，每项只有 {"id": 原样, "text": 译文}，条数、顺序、id 与输入完全一致。**译文必须是${L.name}，不能和英文原文相同**（品牌名、模型 ID、代码本身除外）。

硬规则（脚本会校验）：
1. HTML 标签、属性、顺序、{{N}} 占位符、&amp; 等实体原样保留，只翻译标签之间的文字。<code>…</code> 里的内容一个字不动。
2. 价格、数字、百分比、模型 ID、URL、接口路径、参数名、分辨率（540p/720p/1080p/768P）原样保留。${L.code === 'es' || L.code === 'de' ? '小数点可以写成逗号，但数字本身不能变。' : '小数点保持英文写法。'}
3. 品牌与产品名（见简报）和型号代号不翻译。
4. 不添加原文没有的承诺、数字、功能。不要出现 SLA、可用率、企业专属线路、中国大陆访问、海外信用卡、增值税、对公转账、签合同。原文里若还有中文字符（例如 meta keywords 里的「企业」「发票」），译成目标语言里当地开发者会搜的词，不要保留中文。
5. 语气：${L.tone}
6. title 显示宽度 ≤ ${L.code === 'ja' || L.code === 'ko' ? '64（汉字假名谚文各算 2，约 32 字）' : '65 个字符'}；meta:description ${L.code === 'ja' || L.code === 'ko' ? '约 60–120 字' : '120–160 个字符'}，含模型名、价格，并提到发票（自助开票）。标题和描述里要有当地开发者会搜的词（见简报）。
7. 要像当地人写的文档，不要逐词直译；但意思必须与英文一致。同一概念全部使用简报术语表里的词。
8. 不要写辅助脚本来批量生成译文；直接用 Write 工具写出 JSON 文件（分 2–3 次追加保存也可以，但最终文件必须是完整的一个 JSON 数组）。

写完后运行：python scripts/i18n/check_todo.py ${SERIES} ${L.code} ${c}
ERROR 必须改到 0。不要运行 tm-fill、tm-save、tm-chunks、render、register、prepare、consolidate、resync，也不要删除、移动 drafts/ 下任何文件，也不要修改其他块的文件。
**最后一步必须调用 StructuredOutput** 返回 lang、chunk、items、validateErrors，以及真正需要人判断的地方（notes，最多 3 条）。`

const perLang = async (L) => {
  const done = {}
  for (const wave of WAVES) {
    const t = await parallel(wave.map(c => () => agent(prompt(L, c), { label: `tr:${SERIES}:${L.code}-${c}`, phase: 'Translate', schema: SUMMARY })))
    wave.forEach((c, i) => { done[c] = t[i] || null })
  }
  const failed = CHUNKS.filter(c => !done[c])
  if (failed.length) {
    log(`${SERIES}/${L.code}: 重试 ${failed.join(',')}`)
    const r = await parallel(failed.map(c => () => agent(prompt(L, c), { label: `tr2:${SERIES}:${L.code}-${c}`, phase: 'Translate', schema: SUMMARY })))
    failed.forEach((c, i) => { done[c] = r[i] || null })
  }
  const still = CHUNKS.filter(c => !done[c])
  if (still.length) log(`${SERIES}/${L.code}: 仍失败 ${still.join(',')}`)
  return { lang: L.code, ok: CHUNKS.length - still.length, total: CHUNKS.length, failed: still, notes: CHUNKS.flatMap(c => (done[c] && done[c].notes) || []).slice(0, 12) }
}

phase('Translate')
const out = await parallel(LANGS.map(L => () => perLang(L)))
return out.filter(Boolean)
