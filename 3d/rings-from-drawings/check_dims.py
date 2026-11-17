"""Measure the finished metal meshes and compare with the numbers printed on the drawings."""
import trimesh, numpy as np
RHO925 = 10.36
def inner_radius(m):
    v = m.vertices; r = np.hypot(v[:, 0], v[:, 2]); return r.min()
def thickness_along(m, direction, y=0.0):
    """ray along +-Z from centre: returns (inner hit, outer hit) distance on the shank at axial y"""
    o = np.array([[0, y, 0]]); d = np.array([direction])
    locs, _, _ = m.ray.intersects_location(o, d)
    ds = np.sort(np.linalg.norm(locs - o, axis=1)); return ds
def width_at(m, z, tol=0.15):
    v = m.vertices; sel = np.abs(v[:, 2] - z) < tol; return np.ptp(v[sel, 1])
rows = []
def chk(label, got, want):
    rows.append((label, want, got, got - want))
A = trimesh.load("stl/ring-A-pave-band-metal.stl"); B = trimesh.load("stl/ring-B-twist-metal.stl")
C = trimesh.load("stl/ring-C-oval-solitaire-metal.stl"); D = trimesh.load("stl/ring-D-signet-metal.stl")
# A: plain part of the band (y=+1.5 avoids slot / strip)
up = thickness_along(A, [0, 0, 1], 2.45); dn = thickness_along(A, [0, 0, -1], 2.0)
chk("A top thickness", up[1] - up[0], 1.87); chk("A bottom thickness", dn[1] - dn[0], 1.53); chk("A width", np.ptp(A.vertices[:, 1]), 5.00)
up = thickness_along(B, [0, 0, 1], 1.2); dn = thickness_along(B, [0, 0, -1])
chk("B top thickness", up[1] - up[0], 2.39); chk("B bottom thickness", dn[1] - dn[0], 1.62)
chk("B width at twist", np.ptp(B.vertices[:, 1]), 3.20); chk("B bottom width", width_at(B, B.bounds[0, 2] + 0.05), 2.42)
dn = thickness_along(C, [0, 0, -1]); chk("C bottom thickness", dn[1] - dn[0], 1.62)
chk("C bottom width", width_at(C, C.bounds[0, 2] + 0.5, 0.1), 2.17)
Cs = trimesh.load("stl/ring-C-oval-solitaire-stones.stl")
up = thickness_along(C, [0, 0, 1]); chk("C stone table to finger-hole top", Cs.bounds[1, 2] - up[0], 7.61)
big = max(Cs.split(only_watertight=False), key=lambda s: s.volume)
chk("C centre stone length (Y)", np.ptp(big.vertices[:, 1]), 9.50); chk("C centre stone width (X)", np.ptp(big.vertices[:, 0]), 7.50)
dn = thickness_along(D, [0, 0, -1]); up = thickness_along(D, [0, 0, 1], 0.0)
chk("D inner diameter", 2 * inner_radius(D), 18.42); chk("D top thickness", up[-1] - up[0], 2.26); chk("D bottom thickness", dn[1] - dn[0], 1.54)
chk("D top width", width_at(D, D.bounds[1, 2] - 0.02, 0.03), 3.38); chk("D bottom width", width_at(D, -18.42 / 2, 0.05), 2.37)
print(f"{'check':38s} {'drawing':>8s} {'model':>8s} {'diff':>7s}")
for l, w, g, d in rows: print(f"{l:38s} {w:8.2f} {g:8.2f} {d:+7.2f}")
print()
for n, m, w in (("A", A, 3.802), ("B", B, 2.561), ("C", C, 2.628), ("D", D, 2.557)):
    print(f"ring {n}: watertight={m.is_watertight}  metal {m.volume:6.1f} mm3 -> silver 925 {m.volume*RHO925/1000:5.3f} g  (drawing {w:5.3f} g, {100*(m.volume*RHO925/1000/w-1):+5.1f}%)")

# E: built from the photo + IGA stone report (no drawing) - check the stone and the fixed numbers
E = trimesh.load("stl/ring-E-jade-cabochon-metal.stl"); Es = trimesh.load("stl/ring-E-jade-cabochon-stones.stl")
jade = max(Es.split(only_watertight=False), key=lambda s: s.volume); dn = thickness_along(E, [0, 0, -1])
print()
for l, g, w in (("E jade width (X)", np.ptp(jade.vertices[:, 0]), 18.18), ("E jade length (Y)", np.ptp(jade.vertices[:, 1]), 24.90),
                ("E jade height", np.ptp(jade.vertices[:, 2]), 10.50), ("E jade carat @ SG 3.33", jade.volume * 3.33 / 200, 48.90),
                ("E inner diameter", 2 * inner_radius(E), 58 / np.pi), ("E bottom thickness", dn[1] - dn[0], 2.00),
                ("E bottom width (above 0.6 chamfer)", width_at(E, E.bounds[0, 2] + 0.6, 0.05), 5.50)):
    print(f"{l:38s} {w:8.2f} {g:8.2f} {g - w:+7.2f}")
print(f"ring E: watertight={E.is_watertight}  metal {E.volume:6.1f} mm3 -> silver 925 {E.volume*RHO925/1000:5.2f} g")
