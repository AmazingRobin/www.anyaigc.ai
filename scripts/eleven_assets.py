# 下载并压缩 ElevenLabs 官网素材（2026-11-13 从 elevenlabs.io/zh/v4 取得），输出到 assets/models/eleven/。
# 用法：python scripts/eleven_assets.py   （已存在的文件会跳过；原始文件放在 .tmp/el-raw/，该目录不入库）
# 图片：官网 v4 视觉（橙红 → 绿渐变）用于 v4 / v4 Turbo 首屏；API 页灰色流线图用于其余型号首屏；8 张音色分类图用于使用场景。
# 音频：官网 v4 首屏示例 v4_sept_demo_sample_02（澳洲电台主持人，24 秒），转成 64 kbps 单声道 mp3。
import io
import os
import subprocess
import sys
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, '.tmp', 'el-raw')
OUT = os.path.join(ROOT, 'assets', 'models', 'eleven')
CDN = 'https://eleven-public-cdn.elevenlabs.io/payloadcms/'
GCS = 'https://storage.googleapis.com/eleven-public-cdn/marketing_website/assets/v4-hero/audio/'

# 输出名 -> (原始文件名, 最大宽度, 质量)
IMAGES = {
    'hero-v4.webp': ('thvhyon9wo9-v4-graphic-bg.webp', 1600, 72),
    'hero-mono.webp': ('chb8zu1efs-API-BG.webp', 1600, 70),
    'voice-narration.webp': ('27abtynwxgp-Narration_01.webp', 520, 78),
    'voice-conversational.webp': ('5dn1a57z8es-Conversational_01.webp', 520, 78),
    'voice-social.webp': ('laujwr3f5k-Social_01.webp', 520, 78),
    'voice-character.webp': ('2jm894jv22k-Character_01.webp', 520, 78),
    'voice-education.webp': ('0a1rsf27vgeh-Educational_02.webp', 520, 78),
    'voice-ads.webp': ('al8j3eodiio-Ads_01.webp', 520, 78),
    'voice-entertainment.webp': ('arvd36l5l17-Entertainment_01.webp', 520, 78),
    'voice-multilingual.webp': ('a1pqma28e4-Multilingual_01.webp', 520, 78),
}


def fetch(url, dest):
    if os.path.exists(dest):
        return
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        io.open(dest, 'wb').write(r.read())


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    for name, (raw, width, q) in IMAGES.items():
        dest = os.path.join(OUT, name)
        if os.path.exists(dest):
            continue
        src = os.path.join(RAW, raw)
        fetch(CDN + raw, src)
        im = Image.open(src).convert('RGB')
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dest, 'WEBP', quality=q, method=6)
        print('image', name, im.size, os.path.getsize(dest))
    mp3 = os.path.join(OUT, 'v4-sample.mp3')
    if not os.path.exists(mp3):
        src = os.path.join(RAW, 's02.mp3')
        fetch(GCS + 'v4_sept_demo_sample_02.mp3', src)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-ac', '1', '-b:a', '64k', mp3], check=True)
        print('audio v4-sample.mp3', os.path.getsize(mp3))


if __name__ == '__main__':
    main()
