"""Llama marketplace snapshot, checked 2026-11-11. Prices are USD / 1M tokens.

Source: https://anyaigc.ai/pricing?provider=Ollama (cards and detail drawers).
Keep all displayed decimals; do not calculate prices from the campaign badge.
Llama is developed by Meta; Ollama is the marketplace provider category.
"""
DATE = '2026-11-11'
VERSION = '20261111'
PRICING = 'https://anyaigc.ai/pricing?provider=Ollama'
DOC = 'https://docs.anyaigc.ai/reference/v1/chat/completions'
REGISTER = 'https://anyaigc.ai/register?aff=oOK7&channel=c_wpduopc9'
MODELS = [
    ('llama-3.3-70b-instruct', 'Llama 3.3 70B Instruct', '0.7290', '0.7290', 'llama3.3',
     '面向多轮对话的 70B 指令模型', 'A 70B instruction model for conversation',
     'Llama 3.3 的 70B 指令微调版本，适合对话、资料归纳与文本生成。输入和输出单价相同，便于估算双向用量。',
     'The instruction-tuned 70B Llama 3.3 model supports dialogue, summarization and text generation. Equal input and output rates make mixed workloads easier to budget.'),
    ('llama-3.2-90b-vision-instruct', 'Llama 3.2 90B Vision Instruct', '4.0500', '12.1500', 'llama3.2-vision',
     '将图像理解带进对话', 'Bring image understanding to conversation',
     'Llama 3.2 的 90B 视觉指令模型，面向图像描述、视觉问答与图文理解。可先用本页文本示例完成基础接入。',
     'The 90B Llama 3.2 vision instruction model is designed for image captioning, visual question answering and image-text understanding. Start with the text request below.'),
    ('llama-3.2-11b-vision-instruct', 'Llama 3.2 11B Vision Instruct', '1.3500', '1.3500', 'llama3.2-vision',
     '11B 规模的图文理解模型', 'Image and text understanding at 11B',
     'Llama 3.2 的 11B 视觉指令模型，适合图像描述和围绕图片的问答。与 90B 版本相比，本页型号提供更低的输入与输出单价。',
     'The 11B Llama 3.2 vision instruction model supports image descriptions and questions about images, with lower listed input and output rates than the 90B version.'),
    ('llama-3.2-3b-instruct', 'Llama 3.2 3B Instruct', '0.6750', '0.3375', 'llama3.2',
     '为轻量文本任务选择 3B', 'A compact choice for text workflows',
     'Llama 3.2 的 3B 文本指令模型，适合摘要、改写和给定资料问答。输出按独立单价计费，可按实际任务评估成本。',
     'The 3B Llama 3.2 text instruction model fits summarization, rewriting and questions over supplied material. Its separate output rate helps you budget each workflow.'),
    ('llama-3.2-1b-instruct', 'Llama 3.2 1B Instruct', '0.3375', '0.0844', 'llama3.2',
     '从低成本文本调用开始', 'Start small with low-cost text requests',
     'Llama 3.2 的 1B 文本指令模型，是本页 12 个型号中输入和输出单价最低的选择，适合先验证短文本处理流程。',
     'The 1B Llama 3.2 text instruction model has the lowest listed input and output rates among these 12 models. Use it to prototype concise text-processing tasks.'),
    ('llama-3.1-405b', 'Llama 3.1 405B', '4.0500', '8.1000', 'llama3.1',
     '405B 规模，面向通用语言任务', 'A 405B model for general language tasks',
     'Llama 3.1 的 405B 型号，适合在复杂文本任务中评估更大参数规模的表现。无需自行管理模型部署，通过统一接口调用。',
     'The 405B Llama 3.1 model lets you evaluate a larger model on demanding text tasks through one API, without managing the deployment yourself.'),
    ('llama-3.1-70b', 'Llama 3.1 70B', '2.7000', '5.4000', 'llama3.1',
     '70B 规模的通用文本接入', 'General-purpose text access at 70B',
     'Llama 3.1 的 70B 型号，适合对话与内容处理。可与同代 8B、405B 型号使用相同提示词比较效果与调用成本。',
     'The 70B Llama 3.1 model fits conversation and content processing. Compare it with the same generation’s 8B and 405B models using your own prompts and cost targets.'),
    ('llama-3.1-8b', 'Llama 3.1 8B', '1.3500', '1.3500', 'llama3.1',
     '从 8B 接入 Llama 3.1', 'An 8B entry point to Llama 3.1',
     'Llama 3.1 的 8B 型号，适合文本原型、摘要和基础问答。在统一 API 下切换型号，保留现有消息结构。',
     'The 8B Llama 3.1 model is a starting point for text prototypes, summaries and basic questions. Keep the same message structure when switching models.'),
    ('llama-3-70b', 'Llama 3 70B', '2.7000', '5.4000', 'llama3',
     '保留 Llama 3 的 70B 工作流', 'Keep your Llama 3 70B workflow',
     'Llama 3 的 70B 型号，可用于既有文本任务的接口接入与版本对照。与 Llama 3.1、3.3 是不同型号，请使用完整模型名。',
     'The 70B Llama 3 model supports existing text workflows and version comparisons. It is distinct from Llama 3.1 and 3.3; send the exact model ID.'),
    ('llama-3-8b', 'Llama 3 8B', '1.3500', '1.3500', 'llama3',
     'Llama 3 的 8B 文本模型', 'The 8B text model in Llama 3',
     'Llama 3 的 8B 型号，可作为既有应用的接入选项和版本评估基线。通过消息列表传递上下文，按输入与输出用量结算。',
     'The 8B Llama 3 model is an option for existing applications and a baseline for version comparisons. Send context as messages and pay for input and output usage.'),
    ('llama-2-70b', 'Llama 2 70B', '1.3500', '1.3500', 'llama2',
     '为既有 Llama 2 项目提供接入', 'API access for existing Llama 2 projects',
     'Llama 2 的 70B 型号，适合维护已有提示词与历史评估流程。新项目可同时比较 Llama 3 系列的任务效果与成本。',
     'The 70B Llama 2 model supports established prompts and evaluation workflows. For new projects, compare task quality and cost with the Llama 3 family as well.'),
    ('llama-2-7b', 'Llama 2 7B', '1.3500', '1.3500', 'llama2',
     '为 Llama 2 7B 保留熟悉的接口', 'A familiar interface for Llama 2 7B',
     'Llama 2 的 7B 型号，适合旧版应用接入、文本实验与版本对照。平台按 tokens 计费，无需自行搭建模型运行环境。',
     'The 7B Llama 2 model is available for existing integrations, text experiments and version comparisons. Pay by token usage without setting up a model runtime.'),
]
KEYS = ('id', 'name', 'input', 'output', 'source', 'tag_zh', 'tag_en', 'desc_zh', 'desc_en')
MODELS = [dict(zip(KEYS, row)) for row in MODELS]
BY_ID = {m['id']: m for m in MODELS}
SLUGS = ['llama', *BY_ID]
