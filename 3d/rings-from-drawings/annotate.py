"""Spec-sheet versions of the rings: the ring plus 3D dimension lines and a text panel with every number
from the drawing (dimensions, stones, weights per metal). Text stands in the front plane (X-Z), facing -Y,
so it reads in the front view. Output: stl/<ring>-spec.stl and .3mf (for viewing only, not for casting)."""
import numpy as np, trimesh
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from manifold3d import Manifold, CrossSection, FillRule
from common import union, to_trimesh

FONT = FontProperties(family="DejaVu Sans", weight="bold")
TH = 0.25                                         # relief depth of text and lines

def text(s, x, z, size, y):
    if not s.strip(): return None
    p = TextPath((0, 0), s, size=size, prop=FONT)
    polys = [np.asarray(q) for q in p.to_polygons() if len(q) >= 3]
    if not polys: return None
    m = Manifold.extrude(CrossSection(polys, FillRule.EvenOdd), TH)
    return m.rotate([90, 0, 0]).translate([x, y + TH, z])   # lies in X-Z, faces -Y

def seg(p, q, r=0.07):
    return Manifold.batch_hull([Manifold.sphere(r, 10).translate(p), Manifold.sphere(r, 10).translate(q)])

def arrow(tip, direction, y, L=0.7, w=0.28):
    d = np.asarray(direction, float); d /= np.linalg.norm(d); n = np.array([-d[1], d[0]])
    t = np.asarray(tip, float); b = t - d * L
    pts = [(t[0], y, t[1]), (b[0] + n[0] * w, y, b[1] + n[1] * w), (b[0] - n[0] * w, y, b[1] - n[1] * w)]
    return Manifold.hull_points([(a, yy + o, c) for a, yy, c in pts for o in (0, TH)])

def dim(p, q, label, y, size=1.1, side=(0.4, 0.0), ext=None):
    """dimension between 2D points p,q (x,z) with arrows at both ends, label next to the midpoint"""
    p, q = np.asarray(p, float), np.asarray(q, float); parts = [seg((p[0], y, p[1]), (q[0], y, q[1]))]
    parts += [arrow(p, p - q, y), arrow(q, q - p, y)]
    for a, b in (ext or []):
        parts.append(seg((a[0], y, a[1]), (b[0], y, b[1]), 0.04))
    mid = (p + q) / 2
    parts.append(text(label, mid[0] + side[0], mid[1] + side[1] - size * 0.35, size, y))
    return union([x for x in parts if x is not None])

def panel(lines, x, ztop, y, size=1.15, gap=1.75):
    out = []
    for i, (s, scale) in enumerate(lines):
        m = text(s, x, ztop - i * gap, size * scale, y)
        if m is not None: out.append(m)
    return union(out)

METALS = ["Gold 22K", "Gold 18K", "Gold 14K", "Gold 9K", "Platinum PT", "Silver 925", "Silver", "Copper", "Stainless steel", "Zinc alloy"]
def weight_lines(ws):
    return [("Weight (g) per drawing", 1.0)] + [(f"  {m}  {w:.3f}", 0.95) for m, w in zip(METALS, ws)]

def build(name, ring_full, items, lines, ring_bounds):
    (x0, y0, z0), (x1, y1, z1) = ring_bounds
    yf = y0 - 0.8
    ann = union([f(yf) for f in items])
    pan = panel(lines, x1 + 4.0, z1 + 1.0, yf)
    spec = trimesh.util.concatenate([ring_full, to_trimesh(ann + pan)])
    spec.export(f"stl/{name}-spec.stl")
    sc = trimesh.Scene()
    rf = ring_full.copy(); rf.visual.face_colors = [205, 160, 110, 255]
    an = to_trimesh(ann + pan); an.visual.face_colors = [30, 120, 230, 255]
    sc.add_geometry(rf, geom_name="ring"); sc.add_geometry(an, geom_name="dimensions")
    sc.export(f"stl/{name}-spec.3mf")
    return spec

if __name__ == "__main__":
    L = lambda n: trimesh.load(f"stl/{n}-full.stl")

    # ---------- A ----------
    n = "ring-A-pave-band"; m = L(n); ri = 8.0
    build(n, m, [
        lambda y: dim((-1.2, ri), (-1.2, ri + 1.87), "1.87", y, side=(-1.0, 1.94)),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.53), "1.53", y, side=(-1.0, -2.27)),
        lambda y: dim((-ri, 0), (ri, 0), "ID 16.0 (measured)", y, size=1.0, side=(-6.5, 0.8)),
    ], [("RING A - 5 mm pave band", 1.25), ("Width 5.00 mm", 1), ("Thickness top 1.87 / bottom 1.53 mm", 1),
        ("Inner dia 16.0 mm (measured from drawing)", 1), ("Round 1.10 mm x 23 (sieve 6 li)", 1), ("Round 1.50 mm x 1 (sieve 1.5 fen)", 1),
        ("Round 2.00 mm x 1 (sieve 3.5 fen)", 1), ("", 1)] + weight_lines([6.729, 5.323, 4.752, 4.068, 7.604, 3.802, 3.992, 3.194, 3.015, 2.471])
        + [("This model, silver 925 = 3.886 g", 0.95)], m.bounds)

    # ---------- B ----------
    n = "ring-B-twist"; m = L(n); ri = 8.0
    build(n, m, [
        lambda y: dim((-1.2, ri), (-1.2, ri + 2.39), "2.39", y, side=(-1.0, 2.20)),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.62), "1.62", y, side=(-1.0, -2.31)),
        lambda y: dim((-ri, 0), (ri, 0), "ID 16.0 (measured)", y, size=1.0, side=(-6.5, 0.8)),
    ], [("RING B - twisted band, graduated pave", 1.25), ("Width at twist 3.20 / bottom 2.42 mm", 1), ("Thickness top 2.39 / bottom 1.62 mm", 1),
        ("Inner dia 16.0 mm (measured from drawing)", 1), ("1.10 x2 (6 li), 1.30 x2 (1 fen)", 1), ("1.50 x2 (1.5 fen), 1.70 x2 (2 fen)", 1),
        ("1.80 x4 (2.5 fen) - 12 stones total", 1), ("", 1)] + weight_lines([4.532, 3.585, 3.201, 2.740, 5.121, 2.561, 2.689, 2.151, 2.031, 1.664])
        + [("This model, silver 925 = 2.593 g", 0.95)], m.bounds)

    # ---------- C ----------
    n = "ring-C-oval-solitaire"; m = L(n); ri = 8.25; ztab = ri + 7.61
    build(n, m, [
        lambda y: dim((-6.2, ri), (-6.2, ztab), "7.61", y, side=(-3.4, 0), ext=[((-6.6, ztab), (-3.0, ztab)), ((-6.6, ri), (-1.5, ri))]),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.62), "1.62", y, side=(-1.0, -2.31)),
        lambda y: dim((-ri, 0), (ri, 0), "ID 16.5 (measured)", y, size=1.0, side=(-6.5, 0.8)),
    ], [("RING C - oval solitaire, 4 claws", 1.25), ("Oval 9.50 x 7.50 mm x 1", 1), ("Table to finger hole 7.61 mm", 1),
        ("Bottom thickness 1.62 / width 2.17 mm", 1), ("Inner dia 16.5 mm (measured from drawing)", 1), ("Round 1.00 mm x 14 (5 li) bridge", 1),
        ("Round 1.10 mm x 14 (6 li) hidden halo", 1), ("", 1)] + weight_lines([4.652, 3.680, 3.285, 2.812, 5.257, 2.628, 2.760, 2.208, 2.084, 1.708])
        + [("This model, silver 925 = 2.652 g", 0.95)], m.bounds)

    # ---------- D ----------
    n = "ring-D-signet"; m = L(n); ri = 18.42 / 2
    build(n, m, [
        lambda y: dim((-1.2, ri), (-1.2, ri + 2.26), "2.26", y, side=(-1.0, 2.13)),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.54), "1.54", y, side=(-1.0, -2.27)),
        lambda y: dim((-ri, 0), (ri, 0), "18.42", y, size=1.2, side=(-1.6, 0.8)),
    ], [("RING D - bar signet, single stone", 1.25), ("Inner dia 18.42 mm", 1), ("Thickness top 2.26 / bottom 1.54 mm", 1),
        ("Width top 3.38 / bottom 2.37 mm", 1), ("Top plate length 13.6 mm (measured)", 1), ("Round 2.31 mm x 1 (sieve 5 fen)", 1),
        ("", 1)] + weight_lines([4.526, 3.580, 3.197, 2.736, 5.115, 2.557, 2.685, 2.148, 2.028, 1.662])
        + [("This model, silver 925 = 3.412 g (solid)", 0.95)], m.bounds)
    # ---------- E (from photo + IGA stone report; weights computed from this model) ----------
    n = "ring-E-jade-cabochon"; m = L(n); ri = 19.84 / 2; z0 = ri + 2.40; ztop = z0 + 10.50
    vol = trimesh.load(f"stl/{n}-metal.stl").volume; g925 = vol * 10.36 / 1000
    # metal-to-silver-925 ratios used by the weight tables on the drawings (rings A-D)
    k = [1.770, 1.400, 1.250, 1.070, 2.000, 1.000, 1.050, 0.840, 0.793, 0.650]
    build(n, m, [
        lambda y: dim((-17.0, ri), (-17.0, ztop), f"{ztop - ri:.2f}", y, side=(-3.6, 0),
                      ext=[((-17.4, ztop), (-2.0, ztop)), ((-17.4, ri), (-3.0, ri))]),
        lambda y: dim((-9.09, ztop + 2.2), (9.09, ztop + 2.2), "18.18", y, size=1.2, side=(-1.8, 0.9),
                      ext=[((-9.09, z0 + 1.0), (-9.09, ztop + 2.6)), ((9.09, z0 + 1.0), (9.09, ztop + 2.6))]),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 2.20), "2.20", y, side=(-1.0, -2.6)),
        lambda y: dim((-ri, 0), (ri, 0), "ID 19.84 (US 10)", y, size=1.0, side=(-5.6, 0.8)),
    ], [("RING E - jade cabochon, 4 claws, pave shoulders", 1.25),
        ("Jadeite oval cabochon 24.90 x 18.18 x 10.50 mm", 1), ("48.90 ct, IGA report TG2506120063", 1),
        ("Long axis along the finger", 1), ("Bezel rim 0.85 mm, 1.80 mm high, 4 claws", 1),
        ("Stone top to finger hole 12.90 mm", 1), ("Head 26.70 x 19.98 mm, ring width 28.0 mm", 1),
        ("Shoulder width 24.0 mm, bottom 6.00 x 2.20 mm", 1),
        ("Inner dia 19.84 mm (assumed US 10, change to size)", 1),
        ("Round 1.80 mm x 68 (sieve 2.5 fen), 34 per side", 1), ("", 1),
        ("Weight (g) of this model", 1.0)] + [(f"  {mt}  {g925 * r:.2f}", 0.95) for mt, r in zip(METALS, k)]
        + [(f"Metal volume {vol:.0f} mm3, stone not included", 0.95)], m.bounds)
    print("done")
