# -*- coding: utf-8 -*-
"""Per-model specs for the Llama pages, from Meta's published model cards
(llama.meta.com / Hugging Face, checked 2026-11-14). Context windows are the
length each release was trained with; Meta documents no separate output cap,
so none is stated. Prices stay in llama_data.py.
"""

# context window in tokens
SPECS = {
    "llama-2-7b": dict(params="7B", context=4_096, release=None,
        trained_zh="Llama 2 代，7B 参数，上下文 4,096 tokens。",
        trained_en="A Llama 2 model: 7B parameters and a 4,096-token context."),
    "llama-2-70b": dict(params="70B", context=4_096, release=None,
        trained_zh="Llama 2 代，70B 参数，上下文 4,096 tokens。",
        trained_en="A Llama 2 model: 70B parameters and a 4,096-token context."),
    "llama-3-8b": dict(params="8B", context=8_192, release="2024-04",
        trained_zh="Llama 3 代，8B 参数，上下文 8,192 tokens。",
        trained_en="A Llama 3 model: 8B parameters and an 8,192-token context."),
    "llama-3-70b": dict(params="70B", context=8_192, release="2024-04",
        trained_zh="Llama 3 代，70B 参数，上下文 8,192 tokens。",
        trained_en="A Llama 3 model: 70B parameters and an 8,192-token context."),
    "llama-3.1-8b": dict(params="8B", context=131_072, release="2024-07",
        trained_zh="Llama 3.1 代，8B 参数，上下文 131,072 tokens。",
        trained_en="A Llama 3.1 model: 8B parameters and a 131,072-token context."),
    "llama-3.1-70b": dict(params="70B", context=131_072, release="2024-07",
        trained_zh="Llama 3.1 代，70B 参数，上下文 131,072 tokens。",
        trained_en="A Llama 3.1 model: 70B parameters and a 131,072-token context."),
    "llama-3.1-405b": dict(params="405B", context=131_072, release="2024-07",
        trained_zh="Llama 3.1 代，405B 参数，上下文 131,072 tokens，是本页参数最多的型号。",
        trained_en="A Llama 3.1 model: 405B parameters, the most of any model on this page, and a 131,072-token context."),
    "llama-3.2-1b-instruct": dict(params="1B", context=131_072, release=None,
        trained_zh="Llama 3.2 的 1B 文本指令模型，上下文 131,072 tokens。",
        trained_en="The 1B text instruction model in Llama 3.2, with a 131,072-token context."),
    "llama-3.2-3b-instruct": dict(params="3B", context=131_072, release=None,
        trained_zh="Llama 3.2 的 3B 文本指令模型，上下文 131,072 tokens。",
        trained_en="The 3B text instruction model in Llama 3.2, with a 131,072-token context."),
    "llama-3.2-11b-vision-instruct": dict(params="11B", context=131_072, release="2024-09", vision=True,
        trained_zh="Llama 3.2 的 11B 视觉指令模型，支持图像输入，上下文 131,072 tokens。",
        trained_en="The 11B vision instruction model in Llama 3.2: image input, with a 131,072-token context."),
    "llama-3.2-90b-vision-instruct": dict(params="90B", context=131_072, release="2024-09", vision=True,
        trained_zh="Llama 3.2 的 90B 视觉指令模型，支持图像输入，上下文 131,072 tokens。",
        trained_en="The 90B vision instruction model in Llama 3.2: image input, with a 131,072-token context."),
    "llama-3.3-70b-instruct": dict(params="70B", context=131_072, release="2024-12",
        trained_zh="Llama 3.3 的 70B 指令模型，上下文 131,072 tokens，是本页最新的一代。",
        trained_en="The 70B instruction model in Llama 3.3, the newest generation here, with a 131,072-token context."),
}

# (this, other, zh reason to pick the other, en reason)
ALTS = {
    "llama-2-7b": ("llama-3.2-1b-instruct", "新项目要更长上下文、更低单价时", "for new projects that want a longer context at a lower rate"),
    "llama-2-70b": ("llama-3.3-70b-instruct", "同样是 70B，但要更新一代和更长上下文时", "for the same 70B size in a newer generation with a longer context"),
    "llama-3-8b": ("llama-3.1-8b", "要同样 8B 但上下文从 8,192 提到 131,072 时", "for the same 8B size with the context raised from 8,192 to 131,072"),
    "llama-3-70b": ("llama-3.1-70b", "要同样 70B 但上下文更长时", "for the same 70B size with a longer context"),
    "llama-3.1-8b": ("llama-3.2-3b-instruct", "任务简单、要更低单价时", "when the task is simple and a lower rate matters"),
    "llama-3.1-70b": ("llama-3.3-70b-instruct", "要最新一代的 70B 时", "for the newest 70B generation"),
    "llama-3.1-405b": ("llama-3.3-70b-instruct", "70B 够用、想降低单价时", "when 70B is enough and you want a lower rate"),
    "llama-3.2-1b-instruct": ("llama-3.2-3b-instruct", "要同代里稍大一档的文本模型时", "for the next size up in the same generation"),
    "llama-3.2-3b-instruct": ("llama-3.1-8b", "要更大参数的文本模型时", "when you want a larger text model"),
    "llama-3.2-11b-vision-instruct": ("llama-3.2-90b-vision-instruct", "图像任务要更强效果时", "when image tasks need stronger results"),
    "llama-3.2-90b-vision-instruct": ("llama-3.2-11b-vision-instruct", "图像任务要更低单价时", "when image tasks should cost less"),
    "llama-3.3-70b-instruct": ("llama-3.1-405b", "要参数规模最大的型号时", "when you want the largest parameter count"),
}
