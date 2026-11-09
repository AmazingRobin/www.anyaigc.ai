"""Verified request examples for the MiniMax topic pages.

Only public documentation was read; no billable model requests are performed.
"""

import json


BASE_URL = "https://anyaigc.ai"
DOCS = {
    "text": "https://docs.anyaigc.ai/reference/v1/chat/completions",
    "speech": "https://docs.anyaigc.ai/reference/minimax/v1/t2a_v2?leaf=415373651",
    "video": "https://docs.anyaigc.ai/reference/v1/minimax/v2/video_generation?leaf=c%3A1791537497564",
    "design": "https://docs.anyaigc.ai/reference/minimax/v1/voice_design?leaf=418271561",
}
NOTES = [
    "Voice Design documentation (leaf 418271561) says the response returns "
    "voice_id, but its example is {code: 0, data: {task_id: 'task_example_001'}, "
    "message: 'success'}. Examples therefore print the complete JSON response "
    "without assuming a voice ID, task ID, preview URL, or download flow.",
]


def _payload(lang, model, kind):
    zh = lang == "zh"
    if kind == "text":
        prompt = "请为一个待办应用设计三个清晰的 API 端点。" if zh else "Design three clear API endpoints for a to-do application."
        return "/v1/chat/completions", {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
    if kind == "speech":
        prompt = "你好，欢迎使用 AnyAIGC 语音合成服务。" if zh else "Hello, welcome to speech synthesis with AnyAIGC."
        return "/minimax/v1/t2a_v2", {
            "model": model,
            "text": prompt,
            "voice_setting": {"voice_id": "__MINIMAX_VOICE_ID__"},
        }
    if kind == "video":
        prompt = "海边日落，镜头缓慢推进。" if zh else "A sunset over the sea, with the camera slowly pushing forward."
        return "/minimax/v2/video_generation", {
            "content": [{"text": prompt, "type": "text"}],
            "duration": 5,
            "model": model,
            "ratio": "16:9",
            "resolution": "768P",
        }
    if kind == "design":
        prompt = ("讲述悬疑故事的播音员，声音低沉富有磁性。" if zh else
                  "A suspense-story narrator with a deep, resonant voice.")
        preview = ("夜深了，街上的灯逐一熄灭，远处传来一阵轻轻的敲门声。" if zh else
                   "Night fell, the streetlights went dark, and a soft knock echoed in the distance.")
        return "/minimax/v1/voice_design", {
            "preview_text": preview,
            "prompt": prompt,
            "voice_id": "__MINIMAX_DESIGNED_VOICE_ID__",
        }
    raise ValueError(f"Unknown MiniMax example kind: {kind}")


def _curl(lang, path, payload, kind):
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    headers = (
        f'curl --request POST "{BASE_URL}{path}" \\\n'
        '  --header "Authorization: Bearer $ANYAIGC_API_KEY" \\\n'
        '  --header "Content-Type: application/json" \\\n'
    )
    if kind == "speech":
        comment = (
            "# 将 MINIMAX_VOICE_ID 设为你可使用的音色 ID。\n"
            if lang == "zh"
            else "# Set MINIMAX_VOICE_ID to a voice ID available to your account.\n"
        )
        body = body.replace("__MINIMAX_VOICE_ID__", "${MINIMAX_VOICE_ID}")
        return comment + headers + "  --data @- <<JSON\n" + body + "\nJSON"
    if kind == "design":
        comment = (
            "# 将 MINIMAX_DESIGNED_VOICE_ID 设为你自定义的唯一音色 ID。\n"
            if lang == "zh"
            else "# Set MINIMAX_DESIGNED_VOICE_ID to a unique custom voice ID.\n"
        )
        body = body.replace("__MINIMAX_DESIGNED_VOICE_ID__", "${MINIMAX_DESIGNED_VOICE_ID}")
        return comment + headers + "  --data @- <<JSON\n" + body + "\nJSON"
    return headers + "  --data '" + body + "'"


def _python(lang, path, payload, kind):
    # JSON spelling is valid Python for these verified, scalar-only payloads.
    body = json.dumps(payload, ensure_ascii=False, indent=4)
    body = body.replace('"__MINIMAX_VOICE_ID__"', 'os.environ["MINIMAX_VOICE_ID"]')
    body = body.replace('"__MINIMAX_DESIGNED_VOICE_ID__"', 'os.environ["MINIMAX_DESIGNED_VOICE_ID"]')
    comment = ""
    if kind == "speech":
        comment = (
            "# MINIMAX_VOICE_ID 使用你可调用的音色 ID。\n"
            if lang == "zh"
            else "# MINIMAX_VOICE_ID must be a voice ID available to your account.\n"
        )
    elif kind == "design":
        comment = (
            "# MINIMAX_DESIGNED_VOICE_ID 使用你自定义的唯一音色 ID。\n"
            if lang == "zh"
            else "# MINIMAX_DESIGNED_VOICE_ID must be a unique custom voice ID.\n"
        )
    timeout = 300 if kind in ("speech", "design") else 120
    return (
        "import json\n"
        "import os\n"
        "import urllib.request\n\n"
        f"{comment}payload = {body}\n\n"
        "request = urllib.request.Request(\n"
        f'    "{BASE_URL}{path}",\n'
        '    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),\n'
        "    headers={\n"
        '        "Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"],\n'
        '        "Content-Type": "application/json",\n'
        "    },\n"
        '    method="POST",\n'
        ")\n"
        f"with urllib.request.urlopen(request, timeout={timeout}) as response:\n"
        "    result = json.load(response)\n\n"
        "print(json.dumps(result, ensure_ascii=False, indent=2))"
    )


def examples(lang, model, kind):
    """Return [(label, source)] for static cURL and standard-library Python tabs."""
    if lang not in ("zh", "en"):
        raise ValueError(f"Unsupported example language: {lang}")
    path, payload = _payload(lang, model, kind)
    return [("cURL", _curl(lang, path, payload, kind)),
            ("Python", _python(lang, path, payload, kind))]
