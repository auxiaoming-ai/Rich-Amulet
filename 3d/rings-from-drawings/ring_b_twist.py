"""Ring B - twisted (crossover) band with graduated pave on both sides of a diagonal ribbon.
From drawing: band width 2.42 (bottom), width 3.20 at the twist, top thickness 2.39, bottom thickness 1.62,
stones 1.10 x2, 1.30 x2, 1.50 x2, 1.70 x2, 1.80 x4 (6 per side, small at the ribbon tip, big further out).
Measured from the drawing (scale ~11.4 px/mm): inner dia 16.0, width 3.20 kept over +-50 deg then easing to 2.42,
thickness easing from 2.39 at top to 1.62 by +-70 deg, ribbon edge slope 0.612 crossing the top
(pocket tip 1.25 mm from top centre, full width 6.5 mm from top centre), pave reaching ~+-76 deg (drawing shows ~80)."""
import numpy as np, sys
from common import *

ID, W_BOT, W_TOP, T_TOP, T_BOT = 16.0, 2.42, 3.20, 2.39, 1.62
SIZES = [1.10, 1.30, 1.50, 1.70, 1.80, 1.80]
ri = ID / 2
K, C = 0.612, 3.865            # ribbon edge: y = K (s + C)   (left pocket lies above it)
RIM, DEPTH, END_DEG = 0.20, 0.65, 76.0   # pocket ends 0.3 past the last stone

def W(t):
    a = abs(np.degrees(np.arctan2(np.sin(t), np.cos(t))))
    if a <= 50: return W_TOP
    x = (a - 50) / 130
    return W_BOT + (W_TOP - W_BOT) * (1 + np.cos(np.pi * x)) / 2
def T(t):
    a = abs(np.degrees(np.arctan2(np.sin(t), np.cos(t))))
    c = np.cos(np.pi / 2 * min(a / 70, 1)) ** 2
    return T_BOT + (T_TOP - T_BOT) * c
R_REF = ri + T_TOP
def R(t): return ri + T(t)

def section(t, ch=0.15):
    w, r1 = W(t) / 2, R(t)
    return [(ri, -w + ch), (ri + ch, -w), (r1 - ch, -w), (r1, -w + ch), (r1, w - ch), (r1 - ch, w), (ri + ch, w), (ri, w - ch)][::-1]
loops = [ring_loop(section(t), t) for t in np.linspace(0, 2*np.pi, 721)[:-1]]
metal = sweep(loops)

# ---- pockets (left; right = 180 deg rotation about Z) ----
def y_bounds(s, t):
    hi = W(t) / 2 - RIM
    lo = max(-W(t) / 2 + RIM, K * (s + C))
    return lo, hi
def pocket():
    loops = []
    s_tip = (W_TOP / 2 - RIM) / K - C
    for s in np.linspace(s_tip - 0.03, -np.radians(END_DEG) * R_REF, 160):
        t = s / R_REF; lo, hi = y_bounds(s, t)
        lo = min(lo, hi - 0.02)
        r1 = R(t)
        sec = [(r1 - DEPTH, lo), (r1 - DEPTH, hi), (r1 + 1, hi), (r1 + 1, lo)]
        loops.append(ring_loop(sec, t))
    return sweep(loops, closed=False)
pl = pocket()
pr = pl.rotate([0, 0, 180])
metal = metal - pl - pr

# ---- graduated stones fitted into the pocket ----
def clearance(s, y):
    t = s / R_REF; hi = W(t) / 2 - RIM; lo_rim = -W(t) / 2 + RIM
    d_diag = (y - K * (s + C)) / np.sqrt(1 + K * K)
    return min(hi - y, y - lo_rim, d_diag)
placed = []
s = (W_TOP / 2 - RIM) / K - C
for d in SIZES:
    r = d / 2 + 0.06
    while True:
        s -= 0.01
        ys = np.linspace(-1.6, 1.6, 321)
        cl = np.array([clearance(s, y) for y in ys]); y = ys[cl.argmax()]
        ok = cl.max() >= r and all(np.hypot(s - ps, y - py) >= r + pr_ + 0.10 for ps, py, pr_ in placed)
        if ok: placed.append((s, y, r)); break

stones, cuts, adds = [], [], []
for (s, y, r), d in zip(placed, SIZES):
    for sign in (1, -1):                       # left pocket and its rotated twin
        t = sign * s / R_REF; yy = sign * y
        g = R(t) - 0.10 - stone_height(d)
        cuts.append(on_ring(seat(d), np.degrees(t), g, yy))
        stones.append(on_ring(brilliant(d), np.degrees(t), g, yy))
        for k in range(4):                      # 4 claws per stone
            a = np.radians(45 + 90 * k)
            ds, dy = (d / 2 + 0.08) * np.cos(a), (d / 2 + 0.08) * np.sin(a)
            tt = t + sign * ds / R_REF
            base = R(tt) - DEPTH - 0.05
            claw = Manifold.cylinder(g + stone_height(d) * 0.55 - base, 0.19, 0.16, 16) + \
                   Manifold.sphere(0.18, 16).translate([0, 0, g + stone_height(d) * 0.55 - base])
            adds.append(on_ring(claw, np.degrees(tt), base, yy + sign * dy))
metal = (metal - union(cuts)) + union(adds)
# trim claws that poke outside the band sides
box = Manifold.cube([40, 2 * W_TOP, 40]).translate([-20, -W_TOP, -20])

metal = metal ^ box

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    tm, _ = export("ring-B-twist", metal, stones, out)
    print("placed (s,y):", [(round(a, 2), round(b, 2)) for a, b, _ in placed])
    print("metal vol", round(tm.volume, 2), "watertight", tm.is_watertight, "bbox", np.round(tm.bounds, 2).tolist(), "stones", len(stones))
