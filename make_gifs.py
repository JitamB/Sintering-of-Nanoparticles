"""Combine the snapshots into one GIF per temperature -> images/gifs/sintering_<T>K.gif

Usage: .venv/bin/python make_gifs.py   (run snapshots.py first; times must match)
"""
import os

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
TIMES = {700: [0, 10, 15, 500], 800: [0, 8, 13, 500]}
LABELS = ["start", "contact", "neck formed", "final"]

font, small = ImageFont.truetype(FONT, 34), ImageFont.truetype(FONT, 24)
os.makedirs("images/gifs", exist_ok=True)
for T, ts in TIMES.items():
    frames = []
    for t, lab in zip(ts, LABELS):
        a = Image.open(f"images/{T}K/snap_{T}_{t}ps.png").convert("RGB")
        b = Image.open(f"images/{T}K/snap_{T}_{t}ps_cna.png").convert("RGB")
        w, h = a.size
        f = Image.new("RGB", (2 * w, h + 60), "white")
        f.paste(a, (0, 60))
        f.paste(b, (w, 60))
        d = ImageDraw.Draw(f)
        d.text((30, 12), f"{T} K   t = {t} ps   ({lab})", fill="black", font=font)
        d.text((40, h + 10), "coloured by original particle", fill="black", font=small)
        d.text((w + 40, h + 10), "mid-plane slice, CNA (green = fcc, white = surface/GB)", fill="black", font=small)
        frames.append(f.resize((1400, int(1400 * (h + 60) / (2 * w)))))
    frames[0].save(f"images/gifs/sintering_{T}K.gif", save_all=True, append_images=frames[1:],
                   duration=[1200, 1200, 1200, 2500], loop=0)
    print(f"wrote images/gifs/sintering_{T}K.gif")
