"""Ring C - oval solitaire, 4 tulip claws, hidden halo + stones on both faces of the bridge.
From drawing: oval stone 9.50 x 7.50 x1, round 1.10 x14, round 1.00 x14,
head height 7.61 (stone table to top of finger hole), bottom thickness 1.62, bottom width 2.17.
Measured from the drawing (scale ~12.45 px/mm): inner dia 16.5, side thickness 1.85,
oval long axis along the finger, girdle at 14.7-14.8 above ring centre,
hidden halo rail: outer half-axes 3.6 x 5.2 at girdle-1.1, 14 x 1.10 stones facing outward,
bridge under the head: 7 x 1.00 on the front face + 7 x 1.00 on the back face over +-22 deg,
claws at about +-41.6 deg of the oval (tips 3.2 / 3.6 mm from centre seen from above)."""
import numpy as np, sys
from scipy.interpolate import PchipInterpolator
from common import *

ID, HEAD_H, T_BOT, W = 16.5, 7.61, 1.62, 2.17
SX, SY = 7.50, 9.50
ri = ID / 2
z_table = ri + HEAD_H

# ---- shank ----
tk = PchipInterpolator([0, 20, 40, 60, 90, 180], [1.20, 1.20, 2.20, 2.00, 1.85, T_BOT])
def T(t):
    a = abs(np.degrees(np.arctan2(np.sin(t), np.cos(t)))); return float(tk(a))
def section(t, ch=0.25):
    r1 = ri + T(t); w = W / 2
    return [(ri, -w + ch), (ri + ch, -w), (r1 - ch, -w), (r1, -w + ch), (r1, w - ch), (r1 - ch, w), (ri + ch, w), (ri, w - ch)][::-1]
metal = sweep([ring_loop(section(t), t) for t in np.linspace(0, 2*np.pi, 721)[:-1]])

stones, cuts, adds = [], [], []

# ---- centre stone ----
crown, gir, pav = 0.133, 0.02, 0.43
center = brilliant(SX, 1.0, SY / SX, n=32, crown=crown, girdle=gir, pav=pav)
z_g = z_table - (crown + gir) * SX            # girdle bottom plane
stones.append(center.translate([0, 0, z_g]))
culet = z_g - pav * SX

# ---- hidden-halo rail ----
RA, RB, RZ0, RZ1, RT = 3.60, 5.20, z_g - 1.75, z_g - 0.45, 0.75
def oval_band(a, b, z0, z1, n=180):
    pts = lambda aa, bb, z: [(aa * np.cos(u), bb * np.sin(u), z) for u in np.linspace(0, 2*np.pi, n, endpoint=False)]
    outer = Manifold.hull_points(pts(a, b, z0) + pts(a, b, z1))
    inner = Manifold.hull_points(pts(a - RT, b - RT, z0 - 1) + pts(a - RT, b - RT, z1 + 1))
    return outer - inner
rail = oval_band(RA, RB, RZ0, RZ1)
metal = metal + rail

# ---- claws ----
T0 = np.radians(41.6)
claw_u = [T0, np.pi - T0, np.pi + T0, -T0]
ga, gb = SX / 2, SY / 2
def catmull(P, n=14):
    P = np.asarray(P, float); P = np.vstack([2*P[0]-P[1], P, 2*P[-1]-P[-2]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*s+(2*p0-5*p1+4*p2-p3)*s*s+(-p0+3*p1-3*p2+p3)*s**3))
    out.append(P[-2]); return np.array(out)
def tube(path, r0, r1):
    rs = np.linspace(r0, r1, len(path)); sph = [Manifold.sphere(r, 20).translate(p) for p, r in zip(path, rs)]
    return union([Manifold.batch_hull([a, b]) for a, b in zip(sph[:-1], sph[1:])])
for u in claw_u:
    sx, sy = np.sign(np.cos(u)), np.sign(np.sin(u))
    th = np.radians(48); rmid = ri + 1.0
    P0 = (sx * rmid * np.sin(th), sy * 0.45, rmid * np.cos(th))
    P1 = (sx * 5.2, sy * 1.5, 10.3)
    P2 = (sx * 4.0, sy * 3.0, RZ0 + 0.4)                           # passes the rail
    gx, gy = ga * np.cos(u), gb * np.sin(u)
    P3 = (gx * 1.09, gy * 1.09, z_g + 0.05)                         # outside the girdle
    P4 = (gx * 0.92, gy * 0.92, z_g + 0.62)                         # claw tip over the crown
    adds.append(tube(catmull([P0, P1, P2, P3, P4]), 0.62, 0.40))
    # tie claw into the rail
    adds.append(Manifold.batch_hull([Manifold.sphere(0.5, 16).translate(P2),
                                     Manifold.sphere(0.4, 16).translate((RA * np.cos(u) * 0.98, RB * np.sin(u) * 0.98, (RZ0 + RZ1) / 2))]))
# keep the claws from cutting the stone: seat the stone in the claws
cuts_center = brilliant(SX * 1.005, 1.0, SY / SX, n=32, crown=crown, girdle=gir, pav=pav).translate([0, 0, z_g])

# ---- hidden-halo stones (14 x 1.10) ----
D_H = 1.10; zc = (RZ0 + RZ1) / 2
us = np.linspace(0, 2*np.pi, 4001)
P = np.c_[RA * np.cos(us), RB * np.sin(us)]
arc = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
L = arc[-1]
claw_s = sorted(np.interp(np.mod(c, 2*np.pi), us, arc) for c in claw_u)
gaps = [(claw_s[i], (claw_s[(i+1) % 4] + (L if i == 3 else 0))) for i in range(4)]
lens = [b - a - 1.5 for a, b in gaps]                      # keep 0.75 clear of each claw
alloc = np.round(np.array(lens) / sum(lens) * 14).astype(int); alloc[np.argmax(lens)] += 14 - alloc.sum()
for (a, b), n in zip(gaps, alloc):
    for k in range(n):
        s = a + 0.75 + (b - a - 1.5) * (k + 0.5) / n
        u = np.interp(np.mod(s, L), arc, us)
        p = np.array([RA * np.cos(u), RB * np.sin(u)])
        nrm = np.array([np.cos(u) / RA, np.sin(u) / RB]); nrm /= np.linalg.norm(nrm)
        ang = np.degrees(np.arctan2(nrm[1], nrm[0]))
        depth = stone_height(D_H) - 0.06
        place = lambda m: m.rotate([0, 90, 0]).rotate([0, 0, ang]).translate([p[0] - nrm[0] * depth, p[1] - nrm[1] * depth, zc])
        cuts.append(place(seat(D_H, light=False)))
        stones.append(place(brilliant(D_H)))

# ---- bridge stones (7 front + 7 back, 1.00) ----
D_B = 1.00; rc = ri + 0.60
for k in range(7):
    th = np.radians(-22 + 44 * k / 6)
    for side in (1, -1):
        depth = W / 2 - stone_height(D_B) + 0.06
        place = lambda m: m.rotate([-90 * side, 0, 0]).translate([rc * np.sin(th), side * depth, rc * np.cos(th)])
        cuts.append(place(seat(D_B, light=False)))
        stones.append(place(brilliant(D_B)))
    for side in (1, -1):                                   # claws between bridge stones on both edges
        if k < 6:
            thm = np.radians(-22 + 44 * (k + 0.5) / 6)
            for rr in (ri + 0.12, ri + 1.08):
                adds.append(Manifold.sphere(0.2, 12).translate([rr * np.sin(thm), side * (W / 2 - 0.05), rr * np.cos(thm)]))

metal = (metal + union(adds)) - union(cuts) - cuts_center

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    tm, _ = export("ring-C-oval-solitaire", metal, stones, out)
    print("halo per gap", alloc.tolist(), "culet z", round(culet, 2), "girdle z", round(z_g, 2), "table z", round(z_table, 2))
    print("metal vol", round(tm.volume, 2), "watertight", tm.is_watertight, "bbox", np.round(tm.bounds, 2).tolist(), "stones", len(stones))
