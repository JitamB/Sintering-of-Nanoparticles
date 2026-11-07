"""Smoother GIFs: 20 frames per temperature, dense in the first 20 ps, sparse afterwards.

Usage (from the project folder, after the frames exist):
  for T in 700 800: SNAP_OUT=images/frames/${T}K .venv/bin/python snapshots.py $T <times...>
  .venv/bin/python make_gifs_fluent.py

Reads  images/frames/<T>K/snap_<T>_<t>ps[_cna].png and output/<T>K/neck_<T>.csv (x/R).
Writes images/gifs/sintering_<T>K_fluent.gif            (particle view + CNA slice)
       images/gifs/sintering_<T>K_fluent_particles.gif  (particle view only, no CNA panel)
"""
import csv
import os

from PIL import Image, ImageDraw, ImageFont

TIMES = [0, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 30, 50, 100, 200, 500]
CONTACT = {700: 10, 800: 8}      # from analyze.py
NECK = {700: 15, 800: 13}


def hold(t):
    """Frame duration in ms: quick through the fast events, longer on the late frames."""
    if t <= 20:
        return 400
    return {30: 700, 50: 800, 100: 900, 200: 1000}.get(t, 2500)


def find_font(size):
    for p in ("C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def stage(T, t):
    if t < CONTACT[T]:
        return "approach"
    if t < NECK[T]:
        return "contact"
    if t <= 20:
        return "neck formation"
    if t <= 50:
        return "neck growth"
    return "relaxation"


font, small = find_font(34), find_font(24)
os.makedirs("images/gifs", exist_ok=True)
for T in (700, 800):
    xr = {int(float(r["time_ps"])): float(r["x_over_R"])
          for r in csv.DictReader(open(f"output/{T}K/neck_{T}.csv"))}
    frames, durations = [], []
    for t in TIMES:
        a = Image.open(f"images/frames/{T}K/snap_{T}_{t}ps.png").convert("RGB")
        b = Image.open(f"images/frames/{T}K/snap_{T}_{t}ps_cna.png").convert("RGB")
        w, h = a.size
        f = Image.new("RGB", (2 * w, h + 60), "white")
        f.paste(a, (0, 60))
        f.paste(b, (w, 60))
        d = ImageDraw.Draw(f)
        d.text((30, 12), f"{T} K   t = {t} ps   neck x/R = {xr[t]:.2f}   ({stage(T, t)})", fill="black", font=font)
        d.text((40, h + 10), "coloured by original particle", fill="black", font=small)
        d.text((w + 40, h + 10), "mid-plane slice, CNA (green = fcc, white = surface/GB)", fill="black", font=small)
        frames.append(f.resize((1400, int(1400 * (h + 60) / (2 * w))), Image.LANCZOS))
        durations.append(hold(t))
    # particle-only variant: left half of each frame (no green/white CNA slice)
    solo, solo_dur = [], []
    for t in TIMES:
        a = Image.open(f"images/frames/{T}K/snap_{T}_{t}ps.png").convert("RGB")
        w, h = a.size
        f = Image.new("RGB", (w, h + 60), "white")
        f.paste(a, (0, 60))
        d = ImageDraw.Draw(f)
        d.text((30, 12), f"{T} K   t = {t} ps   neck x/R = {xr[t]:.2f}   ({stage(T, t)})", fill="black", font=font)
        d.text((40, h + 10), "coloured by original particle (blue = particle 1, orange = particle 2)", fill="black", font=small)
        solo.append(f)
        solo_dur.append(hold(t))
    out2 = f"images/gifs/sintering_{T}K_fluent_particles.gif"
    solo[0].save(out2, save_all=True, append_images=solo[1:], duration=solo_dur, loop=0, optimize=True)
    print(f"wrote {out2}  ({len(solo)} frames, {os.path.getsize(out2) / 1e6:.1f} MB)")
    out = f"images/gifs/sintering_{T}K_fluent.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(f"wrote {out}  ({len(frames)} frames, {sum(durations) / 1000:.1f} s, {os.path.getsize(out) / 1e6:.1f} MB)")
