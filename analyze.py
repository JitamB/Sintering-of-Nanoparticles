"""Contact and neck-formation times from LAMMPS logs.

Usage: python3 analyze.py output/700K/log_700.lammps output/800K/log_800.lammps

Contact time : first output where the mid-plane slab contains an atom.
Neck time    : first output where neck radius x >= 0.3 R.
Neck radius  : x = sqrt(N * V_atom / (pi * w)), N = atoms in the slab of width w.
Also writes neck_<T>.csv (time, x/R, Rg) next to each log, for plotting.
"""
import math
import sys

R = 25.0               # particle radius (A)
W = 4.0                # slab width in in.sinter (A)
V_ATOM = 4.05**3 / 4   # volume per atom in fcc Al (A^3)

print(f"{'log':<32}{'contact (ps)':>14}{'neck x>=0.3R (ps)':>20}{'final x/R':>11}{'final Rg (A)':>14}")
for path in sys.argv[1:]:
    rows, cols = [], None
    for line in open(path):
        words = line.split()
        if words[:2] == ["Step", "Time"]:
            cols = words
            continue
        if cols and len(words) == len(cols):
            try:
                rows.append(dict(zip(cols, map(float, words))))
            except ValueError:
                cols = None  # end of thermo block
        elif cols:
            cols = None
    contact = next((r["Time"] for r in rows if r["v_nneck"] > 0), None)
    xr = [math.sqrt(r["v_nneck"] * V_ATOM / (math.pi * W)) / R for r in rows]
    neck = next((r["Time"] for r, x in zip(rows, xr) if x >= 0.3), None)
    with open(path.replace("log_", "neck_").replace(".lammps", ".csv"), "w") as f:
        f.write("time_ps,x_over_R,Rg_A\n")
        for r, x in zip(rows, xr):
            f.write(f"{r['Time']},{x:.4f},{r['c_rg']:.4f}\n")
    print(f"{path:<32}{contact!s:>14}{neck!s:>20}{xr[-1]:>11.2f}{rows[-1]['c_rg']:>14.2f}")
