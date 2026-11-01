"""Quay video dọc 1080x1920 từ chế độ ?film=1 của quán.

Chạy: python tools/render_video.py
Ra file: video/tra-da-via-he.mp4 (không tiếng; thêm nhạc thịnh hành khi đăng TikTok).
"""
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "video"
FRAMES = OUT_DIR / "frames"
FPS = 30
SECONDS = 22


def main():
    if FRAMES.exists():
        shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)
    url = (ROOT / "index.html").as_uri() + "?film=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", args=["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=d3d11"])
        page = browser.new_page(viewport={"width": 540, "height": 960}, device_scale_factor=2)
        page.on("pageerror", lambda e: print("Lỗi trang:", e, file=sys.stderr))
        page.goto(url)
        page.wait_for_function("window.__ready === true", timeout=30000)
        page.evaluate("document.fonts.ready")
        total = FPS * SECONDS
        for i in range(total):
            page.evaluate("__step(1)")
            page.screenshot(path=str(FRAMES / f"f{i:04d}.jpg"), type="jpeg", quality=92)
            if i % 60 == 0:
                print(f"khung {i}/{total}", flush=True)
        browser.close()

    out = OUT_DIR / "tra-da-via-he.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.jpg"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out),
    ], check=True)
    print("Xong:", out)


if __name__ == "__main__":
    main()
