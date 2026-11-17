"""Ring D - bar signet with one flush-set round stone.
Dimensions from drawing: inner dia 18.42, top thickness 2.26, bottom thickness 1.54,
top width 3.38, bottom width 2.37, stone round 2.31 x1.
Measured from the drawing (scale 13.2 px/mm, from the 18.42 dimension):
  flat top length 13.6, side thickness 1.82, stone centre 4.2 left of centre,
  roof ridge rise = 0.25 x width (hexagonal section seen at the bar ends)."""
import numpy as np, sys
from common import *

ID, T_TOP, T_BOT, W_TOP, W_BOT, STONE = 18.42, 2.26, 1.54, 3.38, 2.37, 2.31
T_SIDE, TOP_LEN, STONE_X = 1.82, 13.6, -4.2
ri = ID / 2
z_top = ri + T_TOP
zb = -(ri + T_BOT)

# front-view ridge silhouette: lower ellipse + straight shoulders through the top corners, extended to an apex
def ridge_polygon():
    rx, rz = ri + T_SIDE, ri + T_BOT
    pts = [(rx * np.sin(t), -rz * np.cos(t) if np.cos(t) > 0 else rx * -np.cos(t)) for t in np.linspace(0, 2*np.pi, 721)]
    pts = [(x, z) for x, z in pts]
    cx, cz = TOP_LEN / 2, z_top
    # tangent from corner to ellipse-ish curve: pick curve point that maximises angle (convex hull edge)
    P = np.array(pts)
    from scipy.spatial import ConvexHull
    H = np.vstack([P, [[cx, cz], [-cx, cz]]]); hull = H[ConvexHull(H).vertices]
    # find hull neighbour of right corner below it -> shoulder direction
    i = np.argmin(np.hypot(hull[:, 0] - cx, hull[:, 1] - cz))
    nb = [hull[(i - 1) % len(hull)], hull[(i + 1) % len(hull)]]
    lower = min(nb, key=lambda p: p[1])
    d = np.array([cx, cz]) - lower; apex_z = cz + abs(d[1] / d[0]) * cx
    H2 = np.vstack([hull, [[0, apex_z + 0.01]]])
    return H2[ConvexHull(H2).vertices]

POLY = ridge_polygon()

def R_ridge(t):
    """ray from origin at angle t (from +Z toward +X) to polygon"""
    d = np.array([np.sin(t), np.cos(t)]); best = None
    for a, b in zip(POLY, np.roll(POLY, -1, 0)):
        e = b - a; M = np.array([d, -e]).T
        if abs(np.linalg.det(M)) < 1e-12: continue
        s, u = np.linalg.solve(M, a)
        if s > 0 and -1e-9 <= u <= 1 + 1e-9:
            best = s if best is None else min(best, s)
    return best

def width_at(z):
    # side view: 2.37 across the bottom of the band, 3.38 across the top plate, straight taper in between
    return W_BOT + (W_TOP - W_BOT) * (z - (-ri)) / (z_top - (-ri))

loops = []
for t in np.linspace(0, 2 * np.pi, 361)[:-1]:
    R = R_ridge(t)
    wz = lambda r: width_at(np.clip(r * np.cos(t), -ri, z_top))
    wi = wz(ri); h = 0.25 * wz(R); wo = wz(R - h)
    sec = [(ri, -wi/2), (ri, wi/2), (R - h, wo/2), (R, 0.0), (R - h, -wo/2)]
    loops.append(ring_loop(sec, t))
shank = sweep(loops, closed=True)
metal = shank - Manifold.cube([60, 10, 40]).translate([-30, -5, z_top])   # flat top

stone = brilliant(STONE)
h = stone_height(STONE)
pos = [STONE_X, 0, z_top - h]
metal = metal - seat(STONE).translate(pos)
stones = [stone.translate(pos)]
# bright-cut flush setting: a fine bezel lip is the metal itself (gypsy set); no prongs.

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    tm, _ = export("ring-D-signet", metal, stones, out)
    print("metal vol", round(tm.volume, 2), "watertight", tm.is_watertight, "bbox", np.round(tm.bounds, 2).tolist())
