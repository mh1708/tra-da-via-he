"""Chụp ảnh vuông 1080x1080 từ quán (ảnh đại diện TikTok/CapCut).

Chạy: python tools/render_avatar.py
Ra file: video/avatar-*.png
"""
import math
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "video"

POSES = {
    # Cô Hoa đội nón lá bên quầy trà
    "avatar-co-hoa": {"cam": {"tx": -6.15, "ty": 1.3, "tz": 7.85, "yaw": math.pi + 0.18, "pitch": 0.16, "dist": 1.75}},
    # Code Dạo và chú Tư cụng ly
    "avatar-cung-ly": {"seat": 1, "cup": 90, "act": "cheers", "actAt": 0.55, "npcAct": [1, "cheers", 0.55],
                       "cam": {"tx": -2.95, "ty": 1.0, "tz": 3.05, "yaw": -0.75, "pitch": 0.16, "dist": 2.8}},
}


def main():
    OUT_DIR.mkdir(exist_ok=True)
    url = (ROOT / "index.html").as_uri() + "?film=1"
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", args=["--enable-gpu", "--ignore-gpu-blocklist", "--use-angle=d3d11"])
        for name, pose in POSES.items():
            page = browser.new_page(viewport={"width": 540, "height": 540}, device_scale_factor=2)
            page.goto(url)
            page.wait_for_function("window.__ready === true", timeout=30000)
            page.evaluate("__step(5)")
            page.evaluate("p => __pose(p)", pose)
            page.evaluate("__step(1)")
            page.screenshot(path=str(OUT_DIR / f"{name}.png"))
            page.close()
            print("Xong:", OUT_DIR / f"{name}.png")
        browser.close()


if __name__ == "__main__":
    main()
