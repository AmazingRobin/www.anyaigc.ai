"""Download and compress the official Xiaomi MiMo media selected on 2026-11-09.

Run: python scripts/mimo_assets.py
Sources are public files on mimo.mi.com / mimo.xiaomi.com / Xiaomi CDNs (kept
below for provenance). Raw downloads go to .playwright-mcp/mimo-raw/ (ignored by
git); ffmpeg writes compact webp/mp4 files to assets/models/mimo/. Re-running
skips files that already exist. The logo is lobe-icons `xiaomimimo` (MIT).
"""
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / ".playwright-mcp" / "mimo-raw"
OUT = ROOT / "assets" / "models" / "mimo"
BLOG = "https://mimo.xiaomi.com/mimo-v2-6/assets/"
CDN = "https://mimocode-cdn.xiaomimimo.com/mimocode/blog/mimo-v2-6/"

# local name -> (source url, ffmpeg output args)
IMAGES = {
    # The first-frame poster is a butterfly; the last frame shows the "V2.6" halftone.
    "hero.webp": ("https://mimo.mi.com/images/hero-banner-v5-last-frame.jpg", "scale=1600:-2"),
    "card-pro.webp": ("https://mimo.mi.com/static/model-header-v26-pro.9a1a9eef476b42f0.png", "scale=885:-2"),
    "card-flash.webp": ("https://mimo.mi.com/static/model-header-v26-flash.59175d9df33bbb49.png", "scale=885:-2"),
    "bench-v26.webp": ("https://aistudio-cdn.xiaomimimo.com/xiaomimimo-static/mimo-docs-figures/others/model-v2.6-advantage.png", "scale=1023:-2"),
    "aa-index.webp": (BLOG + "aaindex-trim.png", "scale=1600:-2"),
    "pareto.webp": (BLOG + "pareto.png", "scale=1600:-2"),
    "demo-game.webp": (BLOG + "posters/02.jpg", "scale=960:-2"),
    "demo-sim.webp": (BLOG + "posters/07.jpg", "scale=960:-2"),
    "demo-edit.webp": (BLOG + "posters/19.jpg", "scale=960:-2"),
    "demo-web.webp": (BLOG + "frontend/site-01/poster.jpg", "scale=960:-2"),
    "demo-slides.webp": (BLOG + "slides/deck-01/01.jpg", "scale=960:-2"),
}
VIDEOS = {
    # Hero dot-matrix "V2.6" banner: keep 8 s, 1280 wide, no audio.
    "hero.mp4": ("https://mimo.mi.com/videos/hero-banner-v5.mp4", 1280, 8),
    "demo-sim.mp4": (CDN + "07.mp4", 960, 10),
    "demo-edit.mp4": (CDN + "19.mp4", 960, 10),
}


def download(url):
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / url.rstrip("/").replace("://", "_").replace("/", "_")
    if path.exists():
        return path
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    path.write_bytes(urlopen(request, timeout=120).read())
    return path


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def image(name, url, scale):
    target = OUT / name
    if not target.exists():
        ffmpeg("-i", download(url), "-vf", scale, "-quality", "60" if name == "hero.webp" else "82", "-frames:v", "1", target)
    print(name, target.stat().st_size)


def video(name, url, width, seconds):
    target = OUT / name
    if not target.exists():
        ffmpeg("-i", download(url), "-t", seconds, "-an", "-vf", f"scale={width}:-2,fps=30", "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", target)
    print(name, target.stat().st_size)
    poster = OUT / name.replace(".mp4", "-poster.webp")
    if name != "hero.mp4" and not poster.exists():
        ffmpeg("-i", target, "-frames:v", "1", "-quality", "80", poster)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (url, scale) in IMAGES.items():
        image(name, url, scale)
    for name, (url, width, seconds) in VIDEOS.items():
        video(name, url, width, seconds)


if __name__ == "__main__":
    main()
