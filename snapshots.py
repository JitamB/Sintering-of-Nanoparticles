"""Render OVITO snapshots of traj_<T>.lammpstrj at chosen times.

Usage: .venv/bin/python snapshots.py 700 0 12 16 500   (T, then times in ps)

Reads output/<T>K/traj_<T>.lammpstrj; for each time writes two images into
images/<T>K/ (one dump frame = 1 ps):
  snap_<T>_<t>ps.png        whole system, coloured by original particle (blue / orange)
  snap_<T>_<t>ps_cna.png    6 A slice through the mid-plane (z), coloured by CNA
                            (green = fcc, red = hcp/stacking fault, white = surface/grain boundary)
"""
import os
import sys

from ovito.io import import_file
from ovito.modifiers import (CommonNeighborAnalysisModifier, ComputePropertyModifier,
                             FreezePropertyModifier, SliceModifier)
from ovito.vis import TachyonRenderer, Viewport

T = sys.argv[1]
times = [int(t) for t in sys.argv[2:]]

outdir = f"images/{T}K"
os.makedirs(outdir, exist_ok=True)
pipeline = import_file(f"output/{T}K/traj_{T}.lammpstrj")
pipeline.add_to_scene()
cell = pipeline.source.data.cell
xmid, zmid = cell[0, 3] + cell[0, 0] / 2, cell[2, 3] + cell[2, 2] / 2

# Remember each atom's starting x, colour by which particle it started in
pipeline.modifiers.append(ComputePropertyModifier(output_property="PosX", expressions=["Position.X"]))
pipeline.modifiers.append(FreezePropertyModifier(source_property="PosX",
                                                 destination_property="InitialX", freeze_at=0))
pipeline.modifiers.append(ComputePropertyModifier(
    output_property="Color",
    expressions=[f"InitialX<{xmid} ? 0.25 : 0.95", f"InitialX<{xmid} ? 0.45 : 0.55", f"InitialX<{xmid} ? 0.85 : 0.15"]))

cna = CommonNeighborAnalysisModifier()
cut = SliceModifier(normal=(0, 0, 1), distance=zmid, slab_width=6.0)

vp = Viewport(type=Viewport.Type.Top)
renderer = TachyonRenderer(ambient_occlusion=False)

for t in times:
    for name, extra in ((f"{outdir}/snap_{T}_{t}ps.png", []), (f"{outdir}/snap_{T}_{t}ps_cna.png", [cna, cut])):
        for m in extra:
            pipeline.modifiers.append(m)
        vp.zoom_all()
        vp.render_image(filename=name, size=(1000, 700), frame=t, renderer=renderer)
        for m in extra:
            pipeline.modifiers.remove(m)
        print("wrote", name)
