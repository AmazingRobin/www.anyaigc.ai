# 第 4 批翻译简报：Qwen 系列（ja / ko / es / de）

## 这批是什么
AnyAIGC（API 聚合平台）的 Qwen（阿里云通义千问）系列专题页，共 32 页，读者是开发者，要看价格、接口、怎么接入：
- **对话模型**：Qwen Flash / Plus / Max、Qwen3、Qwen3.5、Qwen3.6、Qwen3.7、Qwen3.8 各型号，部分带 thinking / non-thinking 模式、1M 上下文、多模态（VL、Omni）。
- **Omni / Realtime**：音频输入输出、实时对话（如 qwen3.8-omni-flash-realtime）。
- **图像**：Qwen Image 2.0 / 3.0 / Max 等文生图与图像编辑；Z-Image Turbo。
- **QwQ**：推理模型。
页面讲通过 AnyAIGC 用一个 API Key 调用，走 OpenAI 兼容的 Chat Completions，按百万 tokens 或按张 / 按次计费，并发不限。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、Qwen、Qwen3.8、Alibaba、Alibaba Cloud、Wan、Z-Image、QwQ、Claude、GPT、Gemini、OpenAI
- 型号名与代号：Qwen Flash、Plus、Max、Omni Flash、VL Plus、Image 3.0 Pro 等；A17B、A10B 这类参数量后缀
- 模型 ID 与接口路径：qwen-flash、qwen3.5-397b-a17b、qwen-image-3.0、qwen3.8-omni-flash-realtime 等；所有接口路径与参数名
- 所有代码、命令、JSON 字段、URL、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $
- 规格写法：1M、256K、1,000,000-token 里的数字不改

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。「~12%」这类带波浪线的用「약」。
- **西语**：Business 译 Negocios，Enterprise 译 Empresas。请求统一 petición（不用 solicitud）。「~12%」译「aproximadamente el 12 %」。「300+ modelos」写「más de 300 modelos」。vídeo 带重音。
- **日语**：APIキー（不带空格）。英文没有 about / ~ 的地方不要加「約」，写「定価の12%」；原文有 about / ~ 才用「約」。「1M context」写「コンテキスト長1M」。自助开票写「請求書をセルフサービスで発行」，「Talk to sales」写「営業に問い合わせる」。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。Anfrage（请求）全文统一。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问、海外信用卡；不写增值税、对公转账、签合同。发票只写“在控制台自助开具”。原文没有的承诺不要添加。
- 原文里残留的中文（例如 meta keywords 里的「企业」「发票」）：译成当地开发者会搜的词（法人向け / 기업용 / para empresas / für Unternehmen、請求書 / 인보이스 / factura / Rechnung），不要保留中文。

## 术语（与前几批已复核译文一致，全文只用一个词）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| tokens | トークン | 토큰 | tokens | Tokens |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| context window | コンテキスト長 | 컨텍스트 길이 | ventana de contexto | Kontextfenster |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price | 定価 / 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| thinking / non-thinking mode | 思考モード / 非思考モード | 사고 모드 / 비사고 모드 | modo de razonamiento (thinking) / sin razonamiento | Denkmodus (thinking) / ohne Denkmodus |
| reasoning | 推論 | 추론 | razonamiento | Reasoning |
| multimodal / omnimodal | マルチモーダル / オムニモーダル | 멀티모달 / 옴니모달 | multimodal / omnimodal | multimodal / omnimodal |
| open-weight | オープンウェイト | 오픈 웨이트 | pesos abiertos | offene Gewichte |
| MoE (mixture of experts) | MoE | MoE | MoE | MoE |
| total / active parameters | 総パラメータ / アクティブパラメータ | 전체 / 활성 파라미터 | parámetros totales / activos | Gesamt- / aktive Parameter |
| tool calling / function calling | ツール呼び出し | 도구 호출 | llamada a herramientas | Tool-Aufrufe |
| structured output | 構造化出力 | 구조화된 출력 | salida estructurada | strukturierte Ausgabe |
| cache hit / cached input | キャッシュヒット / キャッシュ入力 | 캐시 히트 / 캐시 입력 | acierto de caché / entrada en caché | Cache-Treffer / zwischengespeicherte Eingabe |
| concurrency / unlimited | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| realtime | リアルタイム | 실시간 | en tiempo real | Echtzeit |
| speech input / output | 音声入力 / 音声出力 | 음성 입력 / 음성 출력 | entrada / salida de voz | Spracheingabe / -ausgabe |
| text-to-image / image editing | テキストから画像 / 画像編集 | 텍스트→이미지 / 이미지 편집 | de texto a imagen / edición de imágenes | Text-zu-Bild / Bildbearbeitung |
| per image / per request | 1枚 / 1リクエストあたり | 이미지당 / 요청당 | por imagen / por petición | pro Bild / pro Anfrage |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| snapshot / dated version | スナップショット | 스냅샷 | instantánea | Snapshot |
| legacy / previous generation | 旧世代 / 前世代 | 이전 세대 | generación anterior | ältere Generation |
| deprecated / retired | 非推奨 / 提供終了 | 지원 중단 / 종료 | obsoleto / retirado | veraltet / eingestellt |
| FAQ 标题 | よくある質問 | 자주 묻는 질문 | Preguntas frecuentes | Häufige Fragen |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词。
- 标题和描述里要有当地开发者会搜的词：日语「Qwen API 料金」；韩语「Qwen API 가격」；西语「API de Qwen precio」；德语「Qwen API Preise」。
- 数字格式：价格和小数一律用小数点（如 0.1985），德语、西语也不用逗号（2026-11-23 用户确认，与英文页、表格、代码、JSON-LD 保持一致）；千分位按各语言习惯写，但不要产生 0,0596 这类逗号小数。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。
- 页面里关于模型局限、官方文档来源的说明，照原意翻，不要弱化也不要加原文没有的承诺。
- 按钮和短标签要短：德语按钮不要超过 28 个字符（手机宽度 390px 下太长会把页面撑宽）。
- hero 打字动画里的 demo prompt（带 caret span）：保持与前几批同类页面一致，译成目标语言，语气用礼貌体（日语「〜してください」）。
