# 第 1 批翻译简报：Gemini / Suno / Midjourney（ja / ko / es / de）

## 这三个系列是什么
AnyAIGC（API 聚合平台）的三组专题页，读者都是开发者，要看价格、接口、怎么接入：
- **Gemini**：Google 的大语言模型（Gemini 3.1 Pro Preview、Gemini 3.8 Flash、Gemini 3.8 Flash TTS、Gemini 4 Argon / Carbon / Hydrogen）。页面讲原生 `/v1beta` 和 OpenAI 兼容 `/v1/chat/completions` 两种接入、按百万 tokens 计费、思考等级（thinking level）、上下文长度。
- **Suno**：AI 音乐生成 API。一句提示词生成带人声的整首歌，另有人声/伴奏分离（stems）、导出 MIDI、歌词、音效。按次计费。
- **Midjourney**：AI 图像生成，通过 HTTP 接口调用：imagine 出四宫格，再放大（upscale）、变体（vary）、拉远（zoom out）、局部重绘等，按次计费。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、Google、Gemini、DeepMind、Suno、Midjourney、Niji、Claude、GPT、OpenAI、Anthropic
- Gemini 型号名：Gemini 3.1 Pro Preview、Gemini 3.8 Flash、Gemini 4 Argon / Carbon / Hydrogen
- 模型 ID 与接口路径：gemini-4-argon、gemini-3.8-flash 等；`/v1beta`、`/v1/chat/completions`、`generateContent`、`/mj/submit/imagine`、`/mj/task/{id}/fetch`
- Midjourney 参数：`--ar`、`--v`、`--niji`、`--stylize` 等，原样放在 `<code>` 里或提示词里，不翻译
- 所有代码、命令、JSON 字段、URL、请求头、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $
- 歌曲示例的标题和歌词（例如 "Last Train of Summer"）若是演示内容，保持原文；风格标签（City Pop、Female Vocal）保持英文

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay，不要音译。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。
- **西语**：Business 译 Negocios；Enterprise 译 Empresas。请求统一用 petición（与已复核译文一致）。「~12%」「about 12%」译「aproximadamente el 12 %」，不要丢掉“约”。
- **日语**：英文原文没有 about / ~ / approximately 的地方，不要加「約」。APIキー（不带空格）。Mythos 之类不涉及本批。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问；不写增值税/对公转账/签合同。发票只写“在控制台自助开具”。原文没有的承诺不要添加。

## 术语（四种语言统一用这些；与 DeepSeek / Claude 已复核译文一致）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| tokens | トークン | 토큰 | tokens | Tokens |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| context window / 1M context | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price（Google 官方定价） | 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| thinking level | 思考レベル（thinking level） | 사고 수준(thinking level) | nivel de razonamiento (thinking level) | Denkstufe (thinking level) |
| native / OpenAI-compatible | ネイティブ / OpenAI互換 | 네이티브 / OpenAI 호환 | nativo / compatible con OpenAI | nativ / OpenAI-kompatibel |
| concurrency / unlimited concurrency | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| per call / per request | 1回あたり | 1회당 | por llamada | pro Aufruf |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| text-to-speech (TTS) | 音声合成（TTS） | 음성 합성(TTS) | síntesis de voz (TTS) | Sprachsynthese (TTS) |
| stems（分轨） | ステム | 스템 | stems | Stems |
| vocals / instrumental | ボーカル / インスト | 보컬 / 반주 | voz / instrumental | Gesang / Instrumental |
| lyrics | 歌詞 | 가사 | letra | Songtext |
| sound effects | 効果音 | 효과음 | efectos de sonido | Soundeffekte |
| upscale / vary / zoom out / inpaint | アップスケール / バリエーション / ズームアウト / 部分修正 | 업스케일 / 변형 / 줌 아웃 / 부분 수정 | ampliar / variar / alejar (zoom out) / repintar | Hochskalieren / Variieren / Herauszoomen / Teilbereich neu zeichnen |
| prompt | プロンプト | 프롬프트 | prompt | Prompt |
| task ID / poll | タスクID / ポーリング | 작업 ID / 폴링 | ID de tarea / sondear (polling) | Task-ID / Polling |
| legacy（旧世代，仍可用） | 旧世代 | 이전 세대 | generación anterior | ältere Generation |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词。
- 标题和描述里要有当地开发者会搜的词：日语「Gemini API 料金」「Suno API」「Midjourney API」；韩语「Gemini API 가격」；西语「API de Gemini precio」；德语「Gemini API Preise」。保留模型名 + API + 价格这个核心。
- 数字格式：德语、西语小数点用逗号（0,1985），日语、韩语保持 0.1985。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。

## 日本（ja）
敬体（です・ます）。「トークン」「コンテキスト」已是通用说法，不必再解释。

## 韩国（ko）
합니다体，技术文档语气，不口语化。价格、计费用「요금」「과금」。

## 西班牙（es）
通用西班牙语，不用西班牙或拉美特有说法。用无人称或统一的 tú，全文一致。

## 德国（de）
标准德语，用 "Sie"。价格用「Preis」，计费用「Abrechnung」。
