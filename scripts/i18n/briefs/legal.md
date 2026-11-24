# 隐私政策、服务条款翻译简报（en / ja / ko / es / de）

## 这是什么
AnyAIGC（API 聚合平台）的《隐私政策》（privacy.html，84 个单元）和《服务协议》（terms.html，96 个单元）。中文是**法律原文，唯一的源**；译文是给海外用户看的对照译本。

输入：`scripts/legal_copy/src.json`，结构 `{"privacy": [{"id": "u0", "kind": "unit", "text": "…"}, …], "terms": […]}`。
输出：`scripts/legal_copy/<lang>.json`，结构 `{"privacy": {"u0": "译文", …}, "terms": {…}}`，**每个 id 都要有，一个不能少，一个不能多**。

## 翻译原则（法律文本）
- **忠实**：一句对一句，不增不减，不改变权利义务、范围、例外和限定词（"除非法律法规要求"、"我们可能"、"不超过"、"包括但不限于"这类词的力度要保持）。不要为了读起来顺而概括、合并、拆成新的条款，也不要补充原文没有的内容、承诺、例子。
- **措辞**：用当地法律文本的正式、中性语体，不用营销腔。同一概念全文只用一个词。
- **不要判断、不要改写法律效果**。遇到你认为有问题或不通的原文，照实译，把问题写进最后的 notes，由人决定。
- 第十条「法律适用与争议解决」里的「有管辖权的人民法院」照实译（例如 "a people's court with jurisdiction at the defendant's place of domicile"），不要改成别国法院，不要加仲裁条款。
- 生效日期（2026 年 1 月 1 日）和版本号（1.1）保持不变，只改日期的写法（如 January 1, 2026 / 2026年1月1日 / 1 de enero de 2026 / 1. Januar 2026）。
- 品牌名 AnyAIGC 大小写固定；"本平台""我们"在译文里统一（en: the Platform / we；日语：本プラットフォーム／当社；韩语：본 플랫폼／저희；西语：la Plataforma／nosotros；德语：die Plattform／wir）。
- 「您」：日语敬体（です・ます）并用「お客様」；韩语合니다体并用「귀하」或「이용자」（全文统一）；西语统一用 usted；德语统一用 Sie；英语用 you。

## 必须原样保留
- HTML 标签、属性、`{{N}}` 之类占位符、`&copy;` 等实体：只翻译标签之间的文字。标签的数量、顺序都不能变。
- 数字和技术词：30 天、TLS/SSL、IP、ID、API Key、1.1 / 8.2 这类小节编号、版本 1.1。
- 网址和邮箱：anyaigc.ai。
- 小节编号：中文「一、二、三…」在译文里一律改成阿拉伯数字加点（1. 2. 3.），目录里和正文里的同一标题必须一模一样（目录链接是锚点，正文标题和目录条目要对得上）；隐私政策本来就是 1. 2. 3.，保持。

## 固定译法（与站点其他页面一致）
| 中文 | English | 日本語 | 한국어 | Español | Deutsch |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 隐私政策 | Privacy Policy | プライバシーポリシー | 개인정보 처리방침 | Política de privacidad | Datenschutzerklärung |
| 服务协议 / 服务条款（同一份文件） | Terms of Service | 利用規約 | 이용약관 | Términos del servicio | Nutzungsbedingungen |
| 首页 | Home | ホーム | 홈 | Inicio | Startseite |
| 模型与价格 | Models & Pricing | モデルと料金 | 모델과 가격 | Modelos y precios | Modelle & Preise |
| 文档 | Docs | ドキュメント | 문서 | Documentación | Doku |
| 一分钟快速接入 | Quick start | クイックスタート | 빠른 시작 | Inicio rápido | Schnellstart |
| 常见问题 | FAQ | よくある質問 | 자주 묻는 질문 | Preguntas frecuentes | Häufige Fragen |
| 法律文档 · Privacy Policy（徽标） | Legal document · Privacy Policy | 法的文書 · Privacy Policy | 법적 문서 · Privacy Policy | Documento legal · Privacy Policy | Rechtsdokument · Privacy Policy |
| 准备开始第一次调用？ | Ready for your first request? | 最初のAPI呼び出しを始めますか？ | 첫 API 호출을 시작할 준비가 되셨나요? | ¿Todo listo para tu primera petición? | Bereit für Ihre erste Anfrage? |
| 注册并创建 API Key | Sign up and create an API key | 登録してAPIキーを作成 | 가입하고 API 키 만들기 | Regístrate y crea una clave de API | Registrieren und API-Schlüssel erstellen |
| 查看模型与价格 | View models and pricing | モデルと料金を見る | 모델과 가격 보기 | Ver modelos y precios | Modelle und Preise ansehen |

最后三行（CTA 区块）的标题和说明文字要和站点首页同一块的译法一致：参考 `scripts/home_copy/<lang>.json` 里的 `final`（en 以外的语言文件如果还没有，就以 en.json 为准自己译）。页脚几个链接的文字同理，参考 `foot.links`。
「服务协议」「服务条款」在中文原页里混用（标题写服务协议，页脚写服务条款），**译文里统一成 Terms of Service 这一个词**。

## 风格检查点
- `<title>`：`隐私政策 - AnyAIGC` → 例如 `Privacy Policy - AnyAIGC`；显示宽度 ≤ 64（日韩汉字假名谚文各算 2）或 ≤ 65 字符。
- meta description（隐私政策那条）：一句话说明政策内容，日韩 60–240 宽度，西德英 120–160 字符；是原文那句的意译，不添加新内容。
- 译文里不要出现任何汉字（日语除外，日语可用汉字）；不要保留中文标点「」。
- 西班牙语用通用西班牙语（不带地区特征），德语用标准德语。
