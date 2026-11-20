# 第 3 批翻译简报：Doubao / Seedream / Seedance / Kimi / GLM / MiMo / MiniMax（ja / ko / es / de）

## 这批是什么
AnyAIGC（API 聚合平台）的七个国产模型系列专题页，共 43 页。读者是开发者，要看价格、接口、怎么接入：
- **Doubao（豆包）**：字节跳动的 Doubao Seed 对话模型（Seed 1.6、1.8、2.0、2.1 的各个型号），带推理、视觉、代码。
- **Seedream**：字节跳动的文生图模型。**Seedance**：字节跳动的视频生成模型（异步任务接口，按生成的 tokens 计费，支持参考图、参考视频、参考音频、首尾帧）。
- **Kimi**：月之暗面（Moonshot AI）的 Kimi K 系列，开放权重的多模态 Agent 模型。
- **GLM**：智谱（Zhipu Z.ai）的 GLM-5 系列，长上下文旗舰。
- **MiMo**：小米（Xiaomi）的 MiMo 模型。
- **MiniMax**：对话与代码（M 系列）、视频（H3 / Hailuo）、语音合成（Speech）、声音设计（Voice Design）。
页面讲通过 AnyAIGC 用一个 API Key 调用，按百万 tokens / 按张 / 按秒 / 按字符计费，价格比官方低一个折扣比例。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、Doubao、Seed、Seedream、Seedance、Kimi、Moonshot AI、GLM、Zhipu、Z.ai、MiMo、Xiaomi、MiniMax、Hailuo、ByteDance、Volcano Engine、Claude、Claude Code、GPT、Gemini、Anthropic、OpenAI
- 型号名与代号：Seed 1.6 Flash、Seed 2.0 Pro、Seedance 2.0 Fast / mini、Kimi K2.6、K3.1、GLM-5.3-Flash、MiMo-V2.5-Pro、MiniMax M3、H3、Voice Design 等
- 模型 ID 与接口路径：doubao-seed-1-6-flash、kimi-k2.6、glm-5.2、minimax-m3 等；所有接口路径与参数名（model、max_tokens、thinking、duration、resolution、ratio、generate_audio、watermark 等）
- 分辨率与规格写法：480p / 720p / 1080p、768P、256K、1M 原样保留
- 所有代码、命令、JSON 字段、URL、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。「~12%」这类带波浪线的用「약」。
- **西语**：Business 译 Negocios，Enterprise 译 Empresas。请求统一 petición（不用 solicitud）。「~12%」译「aproximadamente el 12 %」，不要丢掉"约"。
- **日语**：APIキー（不带空格）。英文原文没有 about / ~ / approximately 的地方，不要加「約」，写「定価の12%」；原文有 about / ~ 的才用「約」。「1Mコンテキスト」统一写「コンテキスト長1M」。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。Anfrage（请求）全文统一。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问、海外信用卡；不写增值税/对公转账/签合同。发票只写"在控制台自助开具"。原文没有的承诺不要添加。
- 原文里残留的中文（例如 meta keywords 里的「企业」「发票」）：译成目标语言里当地开发者会搜的词（法人向け / 기업용 / para empresas / für Unternehmen、請求書 / 인보이스 / factura / Rechnung），不要保留中文。

## 术语（与前几批已复核译文一致，全文只用一个词）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| tokens | トークン | 토큰 | tokens | Tokens |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| context window / 1M context | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price（官方定价） | 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| thinking（模型的思考模式） | 思考モード | 사고 모드 | modo de razonamiento (thinking) | Denkmodus (thinking) |
| reasoning | 推論 | 추론 | razonamiento | Reasoning |
| open-weight | オープンウェイト | 오픈 웨이트 | pesos abiertos | offene Gewichte |
| multimodal / omnimodal | マルチモーダル / オムニモーダル | 멀티모달 / 옴니모달 | multimodal / omnimodal | multimodal / omnimodal |
| agent / sub-agent | エージェント / サブエージェント | 에이전트 / 서브 에이전트 | agente / subagente | Agent / Sub-Agent |
| tool calling | ツール呼び出し | 도구 호출 | llamada a herramientas | Tool-Aufrufe |
| structured output | 構造化出力 | 구조화된 출력 | salida estructurada | strukturierte Ausgabe |
| cached input / cache hit | キャッシュ入力 / キャッシュヒット | 캐시 입력 / 캐시 히트 | entrada en caché / acierto de caché | zwischengespeicherte Eingabe / Cache-Treffer |
| concurrency / unlimited concurrency | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| async task | 非同期タスク | 비동기 작업 | tarea asíncrona | asynchrone Aufgabe |
| reference image / video / audio | 参照画像 / 動画 / 音声 | 참조 이미지 / 비디오 / 오디오 | imagen / vídeo / audio de referencia | Referenzbild / -video / -audio |
| first / last frame | 最初・最後のフレーム | 첫 / 마지막 프레임 | primer / último fotograma | erstes / letztes Frame |
| text-to-image / text-to-video | テキストから画像 / 動画 | 텍스트→이미지 / 비디오 | de texto a imagen / a vídeo | Text-zu-Bild / Text-zu-Video |
| per second / per image / per 10K characters | 1秒 / 1枚 / 1万文字あたり | 초당 / 이미지당 / 1만 자당 | por segundo / por imagen / por 10 000 caracteres | pro Sekunde / pro Bild / pro 10.000 Zeichen |
| speech synthesis (TTS) | 音声合成（TTS） | 음성 합성(TTS) | síntesis de voz (TTS) | Sprachsynthese (TTS) |
| voice design | ボイスデザイン | 보이스 디자인 | diseño de voz | Voice Design |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| legacy（旧世代，仍可用） | 旧世代 | 이전 세대 | generación anterior | ältere Generation |
| deprecated / retired | 非推奨 / 提供終了 | 지원 중단 / 종료 | obsoleto / retirado | veraltet / eingestellt |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词。
- 标题和描述里要有当地开发者会搜的词：日语「Kimi API 料金」；韩语「Kimi API 가격」；西语「API de Kimi precio」；德语「Kimi API Preise」。保留模型名 + API + 价格这个核心。
- 数字格式：德语、西语小数点用逗号（0,3847），日语、韩语保持 0.3847。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。
- 页面里关于模型局限和官方文档来源的说明，照原意翻，不要弱化也不要加原文没有的承诺。
- 按钮和短标签要短：德语按钮不要超过 28 个字符（手机宽度 390px 下太长会把页面撑宽）。

## 日本（ja）
敬体（です・ます）。「トークン」「コンテキスト」已是通用说法，不必再解释。

## 韩国（ko）
합니다体，技术文档语气。价格、计费用「요금」「과금」。

## 西班牙（es）
通用西班牙语，不用西班牙或拉美特有说法。用无人称或统一的 tú，全文一致。

## 德国（de）
标准德语，用 "Sie"。价格用「Preis」，计费用「Abrechnung」。
