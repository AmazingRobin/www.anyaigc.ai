# DeepSeek 系列翻译简报（ja / ko / es / de 通用规则，语言差异见各节）

## 这个系列是什么
DeepSeek（深度求索）的大语言模型 API。页面讲的是通过 AnyAIGC 用一个 API Key 调用这些模型，
按百万 tokens 计费，价格比 DeepSeek 官方低。读者是开发者，要看价格、上下文长度、怎么接入。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、DeepSeek、Claude Code
- 模型 ID：deepseek-v4-flash、deepseek-v4-pro、deepseek-v4.1-flash 等，一律保持原文
- 所有代码、命令、JSON 字段、URL、环境变量 ANYAIGC_API_KEY
- 价格数字与单位换算：原文 "$0.1215 / 1M tokens" 这种数字一个都不能改，货币保持 USD
- 基准测试名：SWE-bench、LiveCodeBench 等保持英文

## 术语（四种语言统一用这些，不要各自发挥）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| API | API | API | API | API |
| tokens | トークン | 토큰 | tokens | Tokens |
| context window / 1M context | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| model catalog（模型广场） | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| rate limit / concurrency | レート制限 / 同時実行数 | 속도 제한 / 동시 실행 | límite de peticiones / concurrencia | Ratenlimit / Parallelität |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要"革命性""最强"这类词（原文也没有）。
- 标题要像当地开发者会搜的样子，例如西语开发者搜 "API de DeepSeek precio"，
  德语搜 "DeepSeek API Preise"，日语搜 "DeepSeek API 料金"，韩语搜 "DeepSeek API 가격"。
  标题里保留模型名 + API + 价格这个核心。
- 折扣说法：保留英文页里的百分比数字（"Save 60%" 里的 60），用当地自然的说法，
  日语「公式価格より約60%お得」，韩语「공식 가격 대비 약 60% 저렴」，西语「un 60 % menos que el precio oficial」，
  德语「rund 60 % günstiger als der offizielle Preis」。不要换算成"4割""六折"这类说法。
- 数字格式按当地习惯：德语、西语用逗号作小数点（0,1215），千分位用点或窄空格；
  日语、韩语保持 0.1215。货币一律写 USD 或 $，不换算成当地货币。

## 日本（ja）
- 敬体（です・ます）。技术术语第一次出现可用日语，括号里保留英文。
- 「トークン」「コンテキスト」已是通用说法，不必再解释。

## 韩国（ko）
- 合니다体（합니다）。技术博客的语气，不要口语化。
- 价格、计费用「요금」「과금」。

## 西班牙（es）
- 通用西班牙语，不用西班牙或拉美特有说法。用 "tú" 但保持专业，或直接用无人称。
- "modelo" 指模型，不要用 "modelo" 指别的东西造成歧义。

## 德国（de）
- 标准德语，用 "Sie"。复合词按德语习惯连写（Kontextfenster、Nutzungsbegrenzung）。
- 价格用「Preis」，计费用「Abrechnung」。
