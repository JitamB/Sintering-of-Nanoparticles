"""Contact and neck checks from the trajectory (pure Python).
Usage: python3 check_contact_neck.py 700
Prints closest P1-P2 distance and bonded pair counts (<3.0/3.4/3.8 A) per ps, and three neck-radius estimates (mid-plane slab, waist, x_rms) as x/R."""
import math, sys, csv
T = sys.argv[1]
N1 = 3997
V = 4.05**3 / 4
R = 25.0
TIMES = set(list(range(0, 21)) + [25, 30, 40, 50, 75, 100, 150, 200, 300, 400, 500])
MAXT = max(TIMES)


def frames(path):
    with open(path) as f:
        k = 0
        while True:
            if not f.readline():
                return
            f.readline(); f.readline(); n = int(f.readline()); f.readline()
            for _ in range(3): f.readline()
            f.readline()
            if k in TIMES:
                yield k, [tuple(map(float, f.readline().split()[2:5])) for _ in range(n)]
                if k >= MAXT: return
            else:
                for _ in range(n): f.readline()
            k += 1


print("T t | min P1-P2 dist | pairs<3.0 <3.4 <3.8 | x_mid(slab@xcm) x_waist(min slab) x_rms(disc) r_max | all /R")
for k, pos in frames(f"output/{T}K/traj_{T}.lammpstrj"):
    xcm = sum(p[0] for p in pos) / len(pos)
    a = [p for i, p in enumerate(pos) if i < N1 and p[0] > xcm - 15]
    b = [p for i, p in enumerate(pos) if i >= N1 and p[0] < xcm + 15]
    dmin = 1e9; c30 = c34 = c38 = 0
    for p in a:
        for q in b:
            d = math.dist(p, q)
            if d < dmin: dmin = d
            if d < 3.0: c30 += 1
            if d < 3.4: c34 += 1
            if d < 3.8: c38 += 1
    out = f"{T} {k:3d} | {dmin:5.2f} | {c30:4d} {c34:4d} {c38:4d} |"
    if k >= 8:
        mid = [p for p in pos if abs(p[0] - xcm) < 2.0]
        x_mid = math.sqrt(len(mid) * V / (math.pi * 4.0))
        # waist: slab of same width, slid +-12 A around xcm, minimum atom count
        best = None
        s = -12.0
        while s <= 12.0:
            sl = [p for p in pos if abs(p[0] - (xcm + s)) < 2.0]
            if best is None or len(sl) < best[0]:
                best = (len(sl), s, sl)
            s += 1.0
        x_waist = math.sqrt(best[0] * V / (math.pi * 4.0))
        sl = best[2]
        if len(sl) > 3:
            yc = sum(p[1] for p in sl) / len(sl); zc = sum(p[2] for p in sl) / len(sl)
            r2 = [(p[1] - yc) ** 2 + (p[2] - zc) ** 2 for p in sl]
            x_rms = math.sqrt(2 * sum(r2) / len(r2))
            rmax = math.sqrt(max(r2))
        else:
            x_rms = rmax = 0.0
        out += f" {x_mid:5.2f} {x_waist:5.2f}@{best[1]:+.0f} {x_rms:5.2f} {rmax:5.2f} | {x_mid/R:.2f} {x_waist/R:.2f} {x_rms/R:.2f}"
    print(out, flush=True)
