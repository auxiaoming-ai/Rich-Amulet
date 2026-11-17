"""Shared helpers for jewellery models. Units: mm.
Frame: finger axis = Y, top of ring = +Z, front view looks along Y (X right, Z up).
Angle theta is measured from +Z toward +X; a point on the ring is (r sin t, y, r cos t)."""
import numpy as np, trimesh
from manifold3d import Manifold, Mesh, OpType

def union(ms):
    ms = [m for m in ms if m is not None]
    return Manifold.batch_boolean(ms, OpType.Add) if len(ms) > 1 else ms[0]

def from_tri(v, f):
    tm = trimesh.Trimesh(np.asarray(v, float), np.asarray(f), process=True)
    if tm.volume < 0:
        tm.invert()
    m = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))
    if m.status().name != "NoError" or m.volume() <= 0:
        raise RuntimeError(f"bad mesh: {m.status()}")
    return m

def sweep(loops, closed=True):
    """loops: list of (K,3) arrays, same K, each a closed polygon. Builds a tube; caps ends if not closed (fan, convex loops)."""
    L = np.asarray(loops, float); n, k = L.shape[:2]
    v = L.reshape(-1, 3); f = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        for a in range(k):
            b = (a + 1) % k
            p, q, r, s = i * k + a, i * k + b, j * k + b, j * k + a
            f += [(p, q, r), (p, r, s)]
    if not closed:
        v = np.vstack([v, L[0].mean(0), L[-1].mean(0)]); c0, c1 = n * k, n * k + 1
        for a in range(k):
            b = (a + 1) % k
            f.append((c0, b, a)); f.append((c1, (n - 1) * k + a, (n - 1) * k + b))
    return from_tri(v, f)

def ring_point(r, y, t):
    return np.array([r * np.sin(t), y, r * np.cos(t)])

def ring_loop(section_ry, t):
    """section in (r, y) -> 3D loop at angle t"""
    return np.array([ring_point(r, y, t) for r, y in section_ry])

def on_ring(m, t_deg, r, y=0.0, tilt_deg=0.0):
    """object built along +Z (base at origin) -> placed on ring surface at angle t, radius r, axial y.
    tilt rotates about the local tangent so the object's axis leans toward +-Y."""
    if tilt_deg:
        m = m.rotate([tilt_deg, 0, 0])
    return m.translate([0, y, r]).rotate([0, t_deg, 0])

# ---------- gemstones (girdle plane at z=0, table up) ----------
def brilliant(d, sx=1.0, sy=1.0, n=16, crown=0.162, girdle=0.03, pav=0.431, table=0.57):
    R = d / 2; pts = [(0, 0, -pav * d)]
    for k in range(n):
        a = 2 * np.pi * k / n
        for z in (0.0, girdle * d):
            pts.append((R * np.cos(a) * sx, R * np.sin(a) * sy, z))
    for k in range(8):
        a = 2 * np.pi * (k + 0.5) / 8
        pts.append((R * table * np.cos(a) * sx, R * table * np.sin(a) * sy, (girdle + crown) * d))
    # star/upper-girdle break points for a facet look
    for k in range(8):
        a = 2 * np.pi * k / 8
        pts.append((R * 0.86 * np.cos(a) * sx, R * 0.86 * np.sin(a) * sy, (girdle + crown * 0.45) * d))
    for k in range(8):
        a = 2 * np.pi * (k + 0.5) / 8
        pts.append((R * 0.5 * np.cos(a) * sx, R * 0.5 * np.sin(a) * sy, -pav * d * 0.62))
    return Manifold.hull_points(pts)

def stone_height(d, crown=0.162, girdle=0.03):
    return (girdle + crown) * d

def seat(d, sx=1.0, sy=1.0, pav=0.431, up=3.0, light=True, clearance=0.05):
    """cutter for a stone seat: girdle bore + pavilion cone + light hole"""
    R = d / 2 + clearance
    bore = Manifold.cylinder(up, R, R, 48).scale([sx, sy, 1]).translate([0, 0, -0.02])
    cone = Manifold.cylinder(pav * d + 0.02, 0.05, R, 48).scale([sx, sy, 1]).translate([0, 0, -pav * d])
    cut = bore + cone
    if light:
        lr = d * 0.27
        cut = cut + Manifold.cylinder(6, lr, lr, 32).scale([sx, sy, 1]).translate([0, 0, -6])
    return cut

def bead(r=0.22):
    return Manifold.sphere(r, 16)

def to_trimesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=True)

def export(name, metal, stones, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    st = union(stones) if stones else None
    tm_metal = to_trimesh(metal)
    tm_full = to_trimesh(metal + st) if st else tm_metal
    tm_metal.export(f"{outdir}/{name}-metal.stl")
    tm_full.export(f"{outdir}/{name}-full.stl")
    if st:
        tm_st = to_trimesh(st); tm_st.export(f"{outdir}/{name}-stones.stl")
        sc = trimesh.Scene(); sc.add_geometry(tm_metal, geom_name="metal"); sc.add_geometry(tm_st, geom_name="stones")
        sc.export(f"{outdir}/{name}.3mf")
    return tm_metal, tm_full

# densities g/cm3 implied by the weight tables (calibrated from ring D, see README)
def report(name, tm_metal, w925_given, rho925):
    vol = tm_metal.volume
    print(f"{name}: watertight={tm_metal.is_watertight} metal vol={vol:.1f} mm3 "
          f"-> 925 weight {vol*rho925/1000:.3f} g (drawing {w925_given:.3f} g, diff {100*(vol*rho925/1000/w925_given-1):+.1f}%) "
          f"bbox={np.round(tm_metal.bounds,2).tolist()}")
