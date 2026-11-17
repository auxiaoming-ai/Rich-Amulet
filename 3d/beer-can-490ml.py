# 490 ml beer can (opened, tab up) -> STL. Units mm. Axis = Z, base at z=0.
import numpy as np, sys, trimesh
from manifold3d import Manifold, CrossSection, OpType
SEG = 180

# half profile (radius, height), counter-clockwise, closed along the axis
prof = [(0, 12), (10, 11.5), (18, 9.5), (23, 6), (24.5, 2), (25, 0), (26.5, 0), (28, 1), (31, 4),
        (32.6, 8), (33, 11), (33, 150), (32.5, 153), (30.5, 158), (29, 162), (28.6, 165),
        (29.2, 166.5), (29.0, 168), (28.0, 168.2), (27.3, 167.5), (26.6, 165), (26.3, 162.2),
        (25.5, 162), (0, 162)]
body = Manifold.revolve(CrossSection([prof]), SEG)

LID = 162
def disc(r, h, x=0, y=0, z=0, sx=1, sy=1):
    return Manifold.cylinder(h, r, r, 64).scale([sx, sy, 1]).translate([x, y, z])

# drinking opening (teardrop) in front of the rivet
opening = Manifold.batch_hull([disc(7.5, 30, y=15, z=LID - 25, sx=1.15), disc(4, 30, y=6.5, z=LID - 25)])
body = body - opening
# shallow ring score around the opening
score = Manifold.batch_hull([disc(8.6, 0.4, y=15, z=LID - 0.3, sx=1.15), disc(5, 0.4, y=6.3, z=LID - 0.3)]) - \
        Manifold.batch_hull([disc(8.1, 0.6, y=15, z=LID - 0.4, sx=1.15), disc(4.5, 0.6, y=6.3, z=LID - 0.4)])
body = body - score

# rivet
rivet = disc(2.6, 0.9, z=LID - 0.1) + Manifold.sphere(1.6, 24).scale([1, 1, 0.5]).translate([0, 0, LID + 0.8])

# pull tab (lifted slightly at the back, nose pressed into the opening)
T = 0.9
tab = Manifold.batch_hull([disc(6.2, T, y=-8.5), disc(5.2, T, y=3.5)])
tab = tab - disc(4.2, 3, y=-9.2, z=-1, sx=1.05, sy=0.75)          # finger hole
tab = tab - disc(1.3, 3, y=-2.3, z=-1, sx=1.6)                     # slot by rivet
tab = tab - (Manifold.batch_hull([disc(5.4, 3, y=-8.5), disc(4.4, 3, y=3.5)]) -
             Manifold.batch_hull([disc(4.8, 3, y=-8.5), disc(3.8, 3, y=3.5)])).translate([0, 0, T * 0.55])  # rolled edge look
tab = tab.translate([0, 0, LID + 0.75]).rotate([-4, 0, 0])

can = Manifold.batch_boolean([body, rivet, tab], OpType.Add)

def tm_of(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=True)

out = sys.argv[1] if len(sys.argv) > 1 else "."
full, tabm = tm_of(can), tm_of(tab)
full.export(f"{out}/beer-can-490ml.stl")
tabm.export(f"{out}/beer-can-tab.stl")
sc = trimesh.Scene(); sc.add_geometry(tm_of(body + rivet), geom_name="can"); sc.add_geometry(tabm, geom_name="tab")
sc.export(f"{out}/beer-can-490ml.3mf"); sc.export(f"{out}/beer-can-490ml.obj")
print("watertight", full.is_watertight, "bbox", full.bounds.round(1).tolist(), "faces", len(full.faces))
