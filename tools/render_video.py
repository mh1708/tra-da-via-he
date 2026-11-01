"""Dựng video dọc 1080x1920 từ các kịch bản trong tools/episodes.json.

Chạy:
  python tools/render_video.py                  # dựng tất cả các tập
  python tools/render_video.py 02 05            # chỉ dựng các tập có id bắt đầu bằng 02, 05
  python tools/render_video.py --preview 02     # chụp vài khung xem trước (540x960) vào video/preview/
Ra file: video/<id>.mp4 (không tiếng; thêm nhạc thịnh hành khi đăng TikTok) và video/posts.md.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "video"
FPS = 30
EPISODES = json.loads((ROOT / "tools" / "episodes.json").read_text(encoding="utf-8"))


def open_page(browser, scale):
    page = browser.new_page(viewport={"width": 540, "height": 960}, device_scale_factor=scale)
    page.on("pageerror", lambda e: print("Lỗi trang:", e, file=sys.stderr))
    page.goto((ROOT / "index.html").as_uri() + "?film=1")
    page.wait_for_function("window.__ready === true", timeout=30000)
    page.evaluate("document.fonts.ready")
    return page


def render(browser, ep):
    frames = OUT_DIR / "frames" / ep["id"]
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    page = open_page(browser, 2)
    page.evaluate("ep => __episode(ep)", ep)
    end, i = ep["duration"] * 1000, 0
    while page.evaluate("__step(1)") <= end:
        page.screenshot(path=str(frames / f"f{i:04d}.jpg"), type="jpeg", quality=92)
        i += 1
    page.close()
    out = OUT_DIR / f"{ep['id']}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "f%04d.jpg"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out),
    ], check=True)
    shutil.rmtree(frames)
    print(f"Xong {out.name}: {i / FPS:.1f} giây", flush=True)


def preview(browser, ep):
    out = OUT_DIR / "preview"
    out.mkdir(parents=True, exist_ok=True)
    page = open_page(browser, 1)
    page.evaluate("ep => __episode(ep)", ep)
    marks = sorted({s["t0"] + 1.2 for s in ep["shots"]} | {ep["duration"] - 0.3} |
                   {c[0] + 0.8 for s in ep["shots"] for c in s.get("caps", [])})
    for m in marks:
        while page.evaluate("__step(1)") < m * 1000:
            pass
        page.screenshot(path=str(out / f"{ep['id']}-{m:05.1f}.jpg"), type="jpeg", quality=80)
    page.close()
    print("Xem trước:", ep["id"], len(marks), "khung", flush=True)


def write_posts():
    lines = ["# Mô tả đăng TikTok\n"]
    for ep in EPISODES:
        lines += [f"## {ep['id']}.mp4", "", ep["desc"], ep["tags"], ""]
    (OUT_DIR / "posts.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    args = sys.argv[1:]
    is_preview = "--preview" in args
    picks = [a for a in args if not a.startswith("--")]
    eps = [e for e in EPISODES if not picks or any(e["id"].startswith(p) for p in picks)]
    OUT_DIR.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", args=["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=d3d11"])
        for ep in eps:
            (preview if is_preview else render)(browser, ep)
        browser.close()
    if not is_preview:
        write_posts()


if __name__ == "__main__":
    main()
