# Project 7 – Sintering of two Al nanoparticles

## Folder layout

```
build.sh  in.sinter  Al99.eam.alloy        inputs
analyze.py  snapshots.py  make_gifs.py     post-processing
structure/      Al_nanoparticles.lmp (+ Atomsk intermediates np1.xsf, np2.xsf)
output/700K/    log_700.lammps  traj_700.lammpstrj  final_700.data  neck_700.csv
output/800K/    same for 800 K
images/700K/    snap_700_<t>ps.png (coloured by particle), snap_700_<t>ps_cna.png (mid-plane slice, CNA)
images/800K/    same for 800 K
images/gifs/    sintering_700K.gif  sintering_800K.gif
```

| File | Purpose |
| :--- | :--- |
| `build.sh` | Atomsk: two R = 25 Å Al spheres, particle 2 rotated 30° about z, ~6.5 Å gap, 160×110×110 Å box → `structure/` |
| `in.sinter` | LAMMPS: minimise → NVT at `T` for 0.5 ns, logs neck atoms (`v_nneck`) and radius of gyration (`c_rg`) → `output/<T>K/` |
| `analyze.py` | Reads the logs → contact time, neck time (x ≥ 0.3R), final x/R and Rg; writes `neck_<T>.csv` next to each log |
| `snapshots.py` | OVITO Python: renders the snapshots → `images/<T>K/` |
| `make_gifs.py` | Combines the snapshots (particle view + CNA slice side by side) → `images/gifs/` |
| `Al99.eam.alloy` | Mishin et al., PRB 59, 3393 (1999), from the NIST potential repository |

## Run (from this folder)

```bash
./build.sh                                                # atomsk is in /opt/homebrew/bin
mpirun -np 6 lmp_mpi -log none -in in.sinter -var T 700   # -log none: no stray log.lammps
mpirun -np 6 lmp_mpi -log none -in in.sinter -var T 800
python3 analyze.py output/700K/log_700.lammps output/800K/log_800.lammps   # comparison table
.venv/bin/python snapshots.py 700 0 10 15 500             # T, then times in ps
.venv/bin/python snapshots.py 800 0 8 13 500
.venv/bin/python make_gifs.py                             # times are set inside the script
```
Quick check before a production run: add `-var NSTEPS 20000` (20 ps, ~1.5 min). Add `-var OUT <folder>` to send the outputs somewhere else, so test runs don't overwrite `output/`.
Run time: a single 6-core job ran at ~20 ns/day (~35 min per run) in testing. The two production runs, started together with 4 cores each, ran at only 1.8 ns/day (~6.6 h each). Run them one after the other.
`.venv` holds the `ovito` (3.17.2) and `pillow` pip packages used by `snapshots.py` and `make_gifs.py`.

## OVITO

1. Load `structure/Al_nanoparticles.lmp` first: two spheres, gap visible, nothing crossing the box edge.
2. Load `output/<T>K/traj_<T>.lammpstrj`, then add these modifiers:
   - **Compute property**: `PosX` = `Position.X`, then **Freeze property**: `PosX` at frame 0 → output `InitialX`. Freezing Position.X directly copies the whole vector.
   - **Color coding**: by `InitialX`. Each particle gets its own colour, so you can see which particle the neck atoms come from.
   - **Common neighbor analysis**: fcc = green, other = white. The grain boundary in the neck and the surfaces show up white. If the fcc fraction drops close to 0, the particle has melted.
   - **Slice** (optional): normal (0,0,1) through the centre, about 5 Å thick, to show the neck cross-section.
3. Take snapshots at t = 0, at contact, at a clear neck, and at the final frame. Use the times printed by `analyze.py`.

## Results (0.5 ns production runs)

| T (K) | Contact time | Neck formation (x ≥ 0.3R) | Final structure (500 ps) |
| :--- | :--- | :--- | :--- |
| 700 | 10 ps | 15 ps | Dumbbell; neck x/R = 0.69 (stopped growing after ~20 ps); Rg 29.5 Å; crystalline (fcc 0.65) |
| 800 | 8 ps | 13 ps | Thicker neck, x/R = 0.85 (still growing to ~350 ps); Rg 28.1 Å, shorter and rounder; crystalline (fcc 0.59) |

- **Neck growth:** at 800 K the neck kept growing for hundreds of ps; at 700 K it stopped after the first ~20 ps. Contact and neck formation are only ~2 ps earlier at 800 K. These are single runs, so that small difference could be noise.
- **No melting:** the fcc fraction stays at 0.5–0.65 throughout at both temperatures.
- **Grain boundary and rotation:** the 30° misorientation creates a grain boundary in the neck (white band in `images/<T>K/snap_<T>_<contact/neck>ps_cna.png`). The particles then rotate into alignment, and the misorientation about z falls to about 1°. This took ~50 ps at 700 K and ~200 ps at 800 K. By 500 ps the neck is fcc at both temperatures.
- **Gap choice:** the Atomsk gap is 7.6 Å between the closest atoms, wider than the 6.29 Å potential cutoff, so contact needs thermal motion. A 4 Å gap tested earlier gave contact in 1–4 ps at both temperatures, with no temperature effect.

## Physics notes (draft for the short explanation)

1. **Why do the particles join?** Surface atoms have missing bonds, so they sit at higher energy. Merging removes surface area and lowers the total energy. In the logs, PE falls by ~100 eV between contact and neck formation.
2. **Why a neck?** At the contact the surface curves inward (negative curvature). By the Gibbs–Thomson relation, this lowers the chemical potential there compared with the convex particle surfaces. Atoms therefore flow into the neck and fill it.
3. **Why does temperature speed it up?** Atom transport is thermally activated: D = D₀ exp(−Q/kT). A higher T means more hops per second, so the neck grows faster. A higher T also gives larger thermal vibrations, which bring the surfaces into contact sooner.
4. **Where do the neck atoms come from?** Mostly from diffusion over the nearby particle surfaces (check the two colours in the neck). There is also some local rearrangement at the new grain boundary. Particle 2 is misoriented by 30°, so a grain boundary forms in the neck. Here the particles rotated by ~30° into alignment, which removed that boundary. MD studies of Cu particles (Zhu & Averback, Phil. Mag. Lett. 73, 27, 1996) reported the same kind of rotation.
5. **Why does this matter for nanoparticles?** They have a huge surface-to-volume ratio, so a large energy can be released. The diffusion distances are tiny. By Herring's scaling law, sintering time scales as Rⁿ (n ≈ 4 for surface diffusion). Nanoparticles also melt at lower temperatures than bulk material. All of this is why they sinter at much lower temperatures than powders, and in picoseconds to nanoseconds here.
