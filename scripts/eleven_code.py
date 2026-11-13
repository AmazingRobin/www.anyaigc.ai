# Eleven 系列专题页的代码示例（中英文共用，代码里不放自然语言注释）。接口：POST https://anyaigc.ai/v1/audio/speech，字段以 docs.anyaigc.ai 为准。
# 注意：接口文档没有写明成功响应的格式；这里按 OpenAI 的 audio/speech 习惯把响应体当作二进制音频保存，交付时需要用户确认。
from eleven_data import VOICE_ID

BS = chr(92)  # 反斜杠


def js(text):
    """放进 JSON / Python 字符串里的文本：转义反斜杠和双引号，换行写成反斜杠 n"""
    return text.replace(BS, BS + BS).replace('"', BS + '"').replace(chr(10), BS + 'n')


def curl(model, text):
    return f'''curl https://anyaigc.ai/v1/audio/speech {BS}
  -H "Authorization: Bearer $ANYAIGC_API_KEY" {BS}
  -H "Content-Type: application/json" {BS}
  -d '{{
    "model": "{model}",
    "input": "{js(text)}",
    "voice": "{VOICE_ID}",
    "response_format": "mp3"
  }}' {BS}
  --output speech.mp3'''


def requests_py(model, text):
    return f'''import os
import requests

resp = requests.post(
    "https://anyaigc.ai/v1/audio/speech",
    headers={{"Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"]}},
    json={{
        "model": "{model}",
        "input": "{js(text)}",
        "voice": "{VOICE_ID}",
        "response_format": "mp3",
    }},
    timeout=120,
)
resp.raise_for_status()
with open("speech.mp3", "wb") as f:
    f.write(resp.content)
print("saved speech.mp3", len(resp.content), "bytes")'''


def sdk_py(model, text):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

with client.audio.speech.with_streaming_response.create(
    model="{model}",
    voice="{VOICE_ID}",
    input="{js(text)}",
    response_format="mp3",
) as response:
    response.stream_to_file("speech.mp3")'''
