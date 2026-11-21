# Eleven 系列专题页的代码示例（中英文共用，代码里不放自然语言注释）。接口：POST https://anyaigc.ai/v1/audio/speech，字段以 docs.anyaigc.ai 为准。
# 注意：接口文档没有写明成功响应的格式；这里按 OpenAI 的 audio/speech 习惯把响应体当作二进制音频保存，交付时需要用户确认。
# 语音转文字（Scribe）示例：POST https://anyaigc.ai/v1/audio/transcriptions，multipart/form-data，只用接口文档（音频转文字 gpt-4o-transcribe）里存在的字段：
# file、model、response_format（language、prompt、temperature 也在文档里，但 scribe 是否按这些字段生效没有核实，示例不用）。200 返回 {"text": "..."}。
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


# ---------------- 语音转文字（Scribe） ----------------
def curl_stt(model):
    return f'''curl https://anyaigc.ai/v1/audio/transcriptions {BS}
  -H "Authorization: Bearer $ANYAIGC_API_KEY" {BS}
  -F file="@meeting.mp3" {BS}
  -F model="{model}"'''


def requests_stt(model):
    return f'''import os
import requests

with open("meeting.mp3", "rb") as f:
    resp = requests.post(
        "https://anyaigc.ai/v1/audio/transcriptions",
        headers={{"Authorization": "Bearer " + os.environ["ANYAIGC_API_KEY"]}},
        files={{"file": f}},
        data={{"model": "{model}"}},
        timeout=600,
    )
resp.raise_for_status()
print(resp.json()["text"])'''


def sdk_stt(model):
    return f'''import os
from openai import OpenAI

client = OpenAI(base_url="https://anyaigc.ai/v1", api_key=os.environ["ANYAIGC_API_KEY"])

with open("meeting.mp3", "rb") as f:
    result = client.audio.transcriptions.create(
        model="{model}",
        file=f,
    )
print(result.text)'''
