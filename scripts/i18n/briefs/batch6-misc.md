# 第 6 批翻译简报：Llama / ElevenLabs / MiniMax Speech / Nano Banana / Jev / SparkDesk / Hy4 / Muse（ja / ko / es / de）

## 这批是什么
AnyAIGC（API 聚合平台）的最后一批专题页，共 42 页（Eleven 的 scribe-v2、scribe-v3 已有译文）。读者是开发者，要看价格、接口、怎么接入：
- **Llama**：Meta 的开源对话模型（Llama 2、3、3.1、3.2、3.3，含 vision 版本）。按百万 tokens 计费。
- **Eleven**：ElevenLabs 的语音模型（Flash v2 / v2.5、Multilingual v2、v3、v4、v3 Conversational），文字转语音，按 1 万字符计费。
- **Speech**：MiniMax Speech 系列（speech-02、2.6、2.8 的 hd / turbo），文字转语音，按 1 万字符计费。
- **Nano Banana**：Google 的图像生成与编辑模型（Nano Banana、2、2.1、Pro），按张计费。
- **Jev**：TypeSafe 的 Jev 模型（jev、1.13.0、1.14.0），输出免费。
- **SparkDesk**：讯飞星火（iFLYTEK）SparkDesk v2.1 / v3.1 / v3.5。
- **Hy4**：腾讯混元 Hy4 / Hy4 Flash。
- **Muse**：Muse Image、Muse Video。
页面讲通过 AnyAIGC 用一个 API Key 调用，走 OpenAI 兼容接口或各自的异步任务接口。厂商名以对应英文页写法为准，不要自己补充英文页没有的厂商信息。

## 必须原样保留（任何语言都不要翻译、不要改写）
- 品牌与产品名：AnyAIGC、Llama、Meta、ElevenLabs、Eleven、MiniMax、Nano Banana、Google、Gemini、Jev、TypeSafe、SparkDesk、iFLYTEK、Hy4、Tencent、Hunyuan、Muse、Claude、GPT、OpenAI
- 型号名与代号：Llama 3.1 405B、Llama 3.2 11B Vision、eleven_v3、eleven_flash_v2_5、speech-02-hd、speech-2.8-turbo、Nano Banana Pro、SparkDesk-v3.5、Hy4 Flash 等
- 模型 ID 与接口路径、参数名（model、voice_id、stability、similarity_boost、speed、emotion、response_format 等）
- 所有代码、命令、JSON 字段、URL、环境变量；价格、百分比、倍数、数字一个都不能改；货币保持 USD / $
- 规格写法：128K、32k context、1M、10K chars、44.1kHz 这类原样保留

## 已确认的译法（四种语言都要遵守）
- **韩语**：微信支付、支付宝写英文原名 WeChat Pay、Alipay。敬体统一「~하세요」，疑问句统一「~입니까/합니까」。list price 译「공식 정가」。「300+」译「300개 이상」。「~12%」这类带波浪线的用「약」。
- **西语**：Business 译 Negocios，Enterprise 译 Empresas。请求统一 petición（不用 solicitud）。「~12%」译「aproximadamente el 12 %」。「300+ models」写「más de 300 modelos」。vídeo 带重音。
- **日语**：APIキー（不带空格）。英文没有 about / ~ 的地方不要加「約」；原文有 about / ~ 才用「約」。自助开票写「請求書をセルフサービスで発行」。
- **德语**：统一用 Sie；复合词连写；「~12%」译「rund 12 %」。Anfrage（请求）全文统一。
- 折扣百分比保留英文页数字，不换算成「N 折」「N割」。
- 不写 SLA、可用率、企业专属线路；不写中国大陆访问、海外信用卡；不写增值税、对公转账、签合同。发票只写“在控制台自助开具”。原文没有的承诺不要添加。
- 原文里残留的中文（例如 meta keywords 里的「企业」「发票」）：译成当地开发者会搜的词（法人向け / 기업용 / para empresas / für Unternehmen、請求書 / 인보이스 / factura / Rechnung），不要保留中文。

## 术语（与前几批已复核译文一致，全文只用一个词）
| 英文 | 日本語 | 한국어 | Español | Deutsch |
| text-to-speech (TTS) | 音声合成（TTS） | 음성 합성(TTS) | síntesis de voz (TTS) | Sprachsynthese (TTS) |
| speech-to-text / transcription | 音声認識 / 文字起こし | 음성 인식 / 전사 | reconocimiento de voz / transcripción | Spracherkennung / Transkription |
| voice / voice cloning | 音声 / ボイスクローン | 음성 / 보이스 클로닝 | voz / clonación de voz | Stimme / Stimmklonung |
| emotion / speaking rate / pitch | 感情 / 話速 / ピッチ | 감정 / 말하기 속도 / 피치 | emoción / velocidad de habla / tono | Emotion / Sprechgeschwindigkeit / Tonhöhe |
| latency | レイテンシ | 지연 시간 | latencia | Latenz |
| per 10K characters | 1万文字あたり | 1만 자당 | por 10 000 caracteres | pro 10.000 Zeichen |
| image generation / image editing | 画像生成 / 画像編集 | 이미지 생성 / 이미지 편집 | generación de imágenes / edición de imágenes | Bildgenerierung / Bildbearbeitung |
| per image | 1枚あたり | 이미지당 | por imagen | pro Bild |
| open-weight | オープンウェイト | 오픈 웨이트 | pesos abiertos | offene Gewichte |
| instruct / chat model | インストラクト / チャットモデル | 인스트럭트 / 채팅 모델 | modelo instruct / de chat | Instruct- / Chat-Modell |
| vision model | ビジョンモデル | 비전 모델 | modelo de visión | Vision-Modell |
| parameters (70B etc.) | パラメータ | 파라미터 | parámetros | Parameter |
| tokens / context window | トークン / コンテキスト長 | 토큰 / 컨텍스트 길이 | tokens / ventana de contexto | Tokens / Kontextfenster |
| per 1M tokens | 100万トークンあたり | 100만 토큰당 | por millón de tokens | pro 1 Mio. Tokens |
| input / output | 入力 / 出力 | 입력 / 출력 | entrada / salida | Eingabe / Ausgabe |
| free output | 出力は無料 | 출력 무료 | salida gratuita | Ausgabe kostenlos |
| API key | APIキー | API 키 | clave de API | API-Schlüssel |
| list price | 定価 / 公式の定価 | 공식 정가 | precio de lista | Listenpreis |
| concurrency / unlimited | 同時実行数 / 上限なし | 동시 실행 / 제한 없음 | concurrencia / sin límite | Parallelität / unbegrenzt |
| async task / polling | 非同期タスク / ポーリング | 비동기 작업 / 폴링 | tarea asíncrona / sondeo | asynchrone Aufgabe / Polling |
| model catalog | モデル一覧 | 모델 카탈로그 | catálogo de modelos | Modellkatalog |
| top up | チャージ | 충전 | recargar saldo | Guthaben aufladen |
| legacy / deprecated / retired | 旧世代 / 非推奨 / 提供終了 | 이전 세대 / 지원 중단 / 종료 | generación anterior / obsoleto / retirado | ältere Generation / veraltet / eingestellt |
| FAQ 标题 | よくある質問 | 자주 묻는 질문 | Preguntas frecuentes | Häufige Fragen |

## 风格
- 开发者文档的语气：直接、具体、短句。不要营销腔，不要原文没有的夸张词，不要夸大音质、画质、速度。
- 标题和描述里要有当地开发者会搜的词：日语「Llama API 料金」；韩语「Llama API 가격」；西语「API de Llama precio」；德语「Llama API Preise」。
- 数字格式：价格和小数一律用小数点（如 0.1985），德语、西语也不用逗号（2026-11-23 用户确认，与英文页、表格、代码、JSON-LD 保持一致）；千分位按各语言习惯写，但不要产生 0,0596 这类逗号小数。
- <title> 显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符（西德）；meta description 日韩 60–240 宽度、西德 120–160 字符，并提到发票（自助开票）。
- 页面里关于模型局限、官方文档来源的说明，照原意翻，不要弱化也不要加原文没有的承诺。
- 按钮和短标签要短：德语按钮不要超过 28 个字符（手机宽度 390px 下太长会把页面撑宽）。
- 旧型号（Llama 2 等）的“已停用”“旧世代”提示，按上面术语表翻，保持语气克制。
- hero 打字动画里的 demo prompt（带 caret span）：译成目标语言，语气用礼貌体（日语「〜してください」），与前几批同类页面一致。
