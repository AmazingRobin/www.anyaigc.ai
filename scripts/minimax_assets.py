"""Download the official MiniMax media selected on 2026-11-09.

Public source URLs and local filenames are kept here for provenance.
No generated image assets are used. The model logo is from lobe-icons (MIT).
"""
from pathlib import Path
import subprocess
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
CDN = 'https://filecdn.minimax.chat/public/'
MEDIA = {
    'hero-text.webp': 'minimax-home-hero-m31-20261017-v1-poster.jpg?x-oss-process=image/format,webp',
    'hero-video.webp': 'minimax-home-hero-h3-20260923-v2-background-poster.jpg?x-oss-process=image/format,webp',
    'card-text.webp': 'minimax-home-model-card-m31-flash-poster-20261017-v3.jpg?x-oss-process=image/format,webp',
    'card-video.webp': 'minimax-home-model-card-h3-poster.png?x-oss-process=image/format,webp',
    'card-speech.webp': 'minimax-home-model-card-speech-poster.png?x-oss-process=image/format,webp',
    'hero-text.mp4': 'minimax-home-hero-m31-20261017-v1-preview.mp4',
    'hero-video.mp4': 'minimax-home-hero-h3-20260923-v2-preview.mp4',
    'hero-speech.mp4': 'minimax-home-model-card-speech-bg.mp4',
}


def download(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60) as response:
        path.write_bytes(response.read())
    print(path.relative_to(ROOT), path.stat().st_size)


if __name__ == '__main__':
    for name, source in MEDIA.items():
        download(CDN + source, ROOT / 'assets/models/minimax' / name)
    # The official speech animation has no full-resolution poster on the home
    # page. Keep its first frame as the matching local reduced-motion fallback.
    poster = ROOT / 'assets/models/minimax/hero-speech.webp'
    if not poster.exists():
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i',
                        str(ROOT / 'assets/models/minimax/hero-speech.mp4'),
                        '-frames:v', '1', '-quality', '85', str(poster)], check=True)
    download('https://registry.npmmirror.com/@lobehub/icons-static-svg/1.97.0/files/icons/minimax-color.svg', ROOT / 'assets/icons/minimax-color.svg')
