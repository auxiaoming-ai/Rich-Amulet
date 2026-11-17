"""Spec-sheet versions of the rings: the ring plus 3D dimension lines and a text panel with every number
from the drawing (dimensions, stones, weights per metal). Text stands in the front plane (X-Z), facing -Y,
so it reads in the front view. Output: stl/<ring>-spec.stl and .3mf (for viewing only, not for casting)."""
import numpy as np, trimesh
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from manifold3d import Manifold, CrossSection, FillRule
from common import union, to_trimesh

FONT = FontProperties(fname="/usr/share/fonts/opentype/tlwg/Loma-Bold.otf")
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

METALS = ["ทอง 22K", "ทอง 18K", "ทอง 14K", "ทอง 9K", "แพลทินัม PT", "เงิน 925", "เงิน", "ทองแดง", "สแตนเลส", "ซิงค์อัลลอย"]
def weight_lines(ws):
    return [("น้ำหนัก (กรัม) ตามแบบ", 1.0)] + [(f"  {m}  {w:.3f}", 0.95) for m, w in zip(METALS, ws)]

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
        lambda y: dim((-ri, 0), (ri, 0), "วงใน 16.0 (วัดจากแบบ)", y, size=1.0, side=(-6.5, 0.8)),
    ], [("แหวน A  พลอยแถว หน้ากว้าง 5 มม.", 1.25), ("หน้ากว้าง 5.00 มม.", 1), ("หนาบน 1.87 / หนาล่าง 1.53 มม.", 1),
        ("วงใน 16.0 มม. (วัดจากสเกลแบบ)", 1), ("เพชร กลม 1.10 x 23 เม็ด (6 ลี้)", 1), ("เพชร กลม 1.50 x 1 เม็ด (1.5 ฟุน)", 1),
        ("เพชร กลม 2.00 x 1 เม็ด (3.5 ฟุน)", 1), ("", 1)] + weight_lines([6.729, 5.323, 4.752, 4.068, 7.604, 3.802, 3.992, 3.194, 3.015, 2.471])
        + [("โมเดลนี้ เงิน 925 = 3.886 ก.", 0.95)], m.bounds)

    # ---------- B ----------
    n = "ring-B-twist"; m = L(n); ri = 8.0
    build(n, m, [
        lambda y: dim((-1.2, ri), (-1.2, ri + 2.39), "2.39", y, side=(-1.0, 2.20)),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.62), "1.62", y, side=(-1.0, -2.31)),
        lambda y: dim((-ri, 0), (ri, 0), "วงใน 16.0 (วัดจากแบบ)", y, size=1.0, side=(-6.5, 0.8)),
    ], [("แหวน B  เกลียวบิด ฝังเพชรไล่ขนาด", 1.25), ("กว้างช่วงบิด 3.20 / กว้างล่าง 2.42 มม.", 1), ("หนาบน 2.39 / หนาล่าง 1.62 มม.", 1),
        ("วงใน 16.0 มม. (วัดจากสเกลแบบ)", 1), ("เพชร 1.10 x2 (6 ลี้)   1.30 x2 (1 ฟุน)", 1), ("เพชร 1.50 x2 (1.5 ฟุน) 1.70 x2 (2 ฟุน)", 1),
        ("เพชร 1.80 x4 (2.5 ฟุน)   รวม 12 เม็ด", 1), ("", 1)] + weight_lines([4.532, 3.585, 3.201, 2.740, 5.121, 2.561, 2.689, 2.151, 2.031, 1.664])
        + [("โมเดลนี้ เงิน 925 = 2.593 ก.", 0.95)], m.bounds)

    # ---------- C ----------
    n = "ring-C-oval-solitaire"; m = L(n); ri = 8.25; ztab = ri + 7.61
    build(n, m, [
        lambda y: dim((-6.2, ri), (-6.2, ztab), "7.61", y, side=(-3.4, 0), ext=[((-6.6, ztab), (-3.0, ztab)), ((-6.6, ri), (-1.5, ri))]),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.62), "1.62", y, side=(-1.0, -2.31)),
        lambda y: dim((-ri, 0), (ri, 0), "วงใน 16.5 (วัดจากแบบ)", y, size=1.0, side=(-6.5, 0.8)),
    ], [("แหวน C  เม็ดไข่ หนามเตย 4 ขา", 1.25), ("เพชรเม็ดไข่ 9.50 x 7.50 มม. x 1", 1), ("หน้าเพชรถึงขอบรูนิ้ว 7.61 มม.", 1),
        ("หนาล่าง 1.62 / กว้างล่าง 2.17 มม.", 1), ("วงใน 16.5 มม. (วัดจากสเกลแบบ)", 1), ("เพชร กลม 1.00 x 14 (5 ลี้) ที่สะพาน", 1),
        ("เพชร กลม 1.10 x 14 (6 ลี้) ฮาโลซ่อน", 1), ("", 1)] + weight_lines([4.652, 3.680, 3.285, 2.812, 5.257, 2.628, 2.760, 2.208, 2.084, 1.708])
        + [("โมเดลนี้ เงิน 925 = 2.652 ก.", 0.95)], m.bounds)

    # ---------- D ----------
    n = "ring-D-signet"; m = L(n); ri = 18.42 / 2
    build(n, m, [
        lambda y: dim((-1.2, ri), (-1.2, ri + 2.26), "2.26", y, side=(-1.0, 2.13)),
        lambda y: dim((-1.2, -ri), (-1.2, -ri - 1.54), "1.54", y, side=(-1.0, -2.27)),
        lambda y: dim((-ri, 0), (ri, 0), "18.42", y, size=1.2, side=(-1.6, 0.8)),
    ], [("แหวน D  แหวนบาร์ เพชรเม็ดเดี่ยว", 1.25), ("วงใน 18.42 มม.", 1), ("หนาบน 2.26 / หนาล่าง 1.54 มม.", 1),
        ("กว้างบน 3.38 / กว้างล่าง 2.37 มม.", 1), ("หน้าบาร์ยาว 13.6 มม. (วัดจากแบบ)", 1), ("เพชร กลม 2.31 x 1 เม็ด (5 ฟุน)", 1),
        ("", 1)] + weight_lines([4.526, 3.580, 3.197, 2.736, 5.115, 2.557, 2.685, 2.148, 2.028, 1.662])
        + [("โมเดลนี้ เงิน 925 = 3.412 ก. (ตันกว่าแบบ)", 0.95)], m.bounds)
    print("done")
