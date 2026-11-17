# Oval solitaire ring with pave band -> STL (units: mm)
# Finger axis = Y, stone on top (+Z)
import numpy as np, sys
from manifold3d import Manifold, CrossSection

SEG = 96
INNER_D = 17.3          # ring size ~ US 7 / TH 54
BAND_W = 1.8            # width along finger
BAND_T = 1.5            # metal thickness
STONE_X, STONE_Y = 6.0, 8.0   # oval stone 8x6 mm (long side along finger)
PAVE_D = 1.1

ri = INNER_D / 2
ro = ri + BAND_T

# ---------- band ----------
cs = CrossSection.square([BAND_T, BAND_W]).translate([ri, -BAND_W / 2])
cs = cs.offset(-0.35, circular_segments=24).offset(0.35, circular_segments=24)
band = Manifold.revolve(cs, SEG).rotate([90, 0, 0])   # axis along Y

def place(m, theta_deg, r):
    """put object built along +Z at angle theta (from top) on circle radius r in XZ plane"""
    return m.translate([0, 0, r]).rotate([0, theta_deg, 0])

# ---------- pave stones + beads ----------
def brilliant(d, n=8):
    rr = d / 2
    pts = [(0, 0, -0.43 * d)]                       # culet
    for k in range(n * 2):                           # girdle
        a = np.pi * k / n
        pts.append((rr * np.cos(a), rr * np.sin(a), 0))
    for k in range(n):                               # table
        a = np.pi * (2 * k + 1) / n
        pts.append((0.55 * rr * np.cos(a), 0.55 * rr * np.sin(a), 0.16 * d))
    return Manifold.hull_points(pts)

stone_small = brilliant(PAVE_D)
bead = Manifold.sphere(0.22, 16)
step = np.degrees((PAVE_D + 0.18) / ro)
pave = []
for side in (1, -1):
    for i in range(11):
        th = side * (16 + i * step)
        seat = Manifold.cylinder(1.0, PAVE_D / 2 + 0.05, PAVE_D / 2 + 0.05, 24).translate([0, 0, -0.4])
        band = band - place(seat, th, ro)
        pave.append(place(stone_small.translate([0, 0, -0.05]), th, ro))
        for yy in (-0.62, 0.62):
            pave.append(place(bead.translate([0, yy, 0.0]), th + side * step / 2, ro))

# ---------- centre oval stone ----------
a, b = STONE_X / 2, STONE_Y / 2
pav_depth, crown_h = 0.43 * STONE_X, 0.15 * STONE_X
girdle_z = ro + 0.35 + pav_depth
def oval_stone():
    pts = [(0, -0.3, girdle_z - pav_depth), (0, 0.3, girdle_z - pav_depth)]
    n = 16
    for k in range(n * 2):
        t = np.pi * k / n
        pts.append((a * np.cos(t), b * np.sin(t), girdle_z))
        pts.append((a * np.cos(t), b * np.sin(t), girdle_z + 0.12))
    for k in range(n):
        t = np.pi * (2 * k + 1) / n
        pts.append((0.72 * a * np.cos(t), 0.72 * b * np.sin(t), girdle_z + 0.12 + 0.55 * crown_h))
    for k in range(8):
        t = np.pi * (2 * k) / 8
        pts.append((0.55 * a * np.cos(t), 0.55 * b * np.sin(t), girdle_z + 0.12 + crown_h))
    return Manifold.hull_points(pts)
stone = oval_stone()

# ---------- basket: gallery rail + 4 claw prongs ----------
def oval_wire(sx, sy, z, wire, n=48):
    pts = [Manifold.sphere(wire, 16).translate([sx*np.cos(2*np.pi*k/n), sy*np.sin(2*np.pi*k/n), z]) for k in range(n)]
    return Manifold.batch_boolean([Manifold.batch_hull([pts[k], pts[(k+1) % n]]) for k in range(n)], __import__('manifold3d').OpType.Add)

rail_z = girdle_z - 1.1
rail = oval_wire(a * 0.8, b * 0.8, rail_z, 0.3)

prongs = []
pr = 0.45
for t in (52, 128, 232, 308):
    tr = np.radians(t)
    gx, gy = a * np.cos(tr), b * np.sin(tr)
    base = Manifold.sphere(pr, 20).translate([np.sign(gx) * 1.0, np.sign(gy) * 0.55, ro - 0.3])
    mid = Manifold.sphere(pr, 20).translate([gx * 1.04, gy * 1.04, girdle_z])
    tip = Manifold.sphere(0.32, 20).translate([gx * 0.9, gy * 0.9, girdle_z + 0.75])
    prongs.append(Manifold.batch_hull([base, mid]))
    prongs.append(Manifold.batch_hull([mid, tip]))

# cut stone seat out of prongs so stone sits in them
metal = Manifold.batch_boolean([band, rail] + prongs + pave, __import__('manifold3d').OpType.Add)
ring = metal + stone

import trimesh
def tm_of(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=True)
if "--parts" in sys.argv:
    d = sys.argv[sys.argv.index("--parts") + 1]
    metal_tm, stone_tm, full_tm = tm_of(metal), tm_of(stone), tm_of(ring)
    full_tm.export(f"{d}/ring-full.stl")
    metal_tm.export(f"{d}/ring-metal.stl"); stone_tm.export(f"{d}/ring-center-stone.stl")
    sc = trimesh.Scene(); sc.add_geometry(metal_tm, node_name="metal", geom_name="metal"); sc.add_geometry(stone_tm, node_name="stone", geom_name="stone")
    sc.export(f"{d}/ring-3d.3mf"); sc.export(f"{d}/ring-3d.obj")
    for n, t in [("metal", metal_tm), ("stone", stone_tm), ("full", full_tm)]:
        print(n, "watertight", t.is_watertight, "vol", round(t.volume, 1))
    sys.exit()

mesh = ring.to_mesh()
v = np.asarray(mesh.vert_properties)[:, :3]
f = np.asarray(mesh.tri_verts)
import trimesh
tm = trimesh.Trimesh(v, f, process=True)
print("watertight:", tm.is_watertight, "faces:", len(f), "bbox:", tm.bounds.round(2).tolist(), "vol mm3:", round(tm.volume, 1))
out = sys.argv[1] if len(sys.argv) > 1 else "ring.stl"
tm.export(out)
print("saved", out)
