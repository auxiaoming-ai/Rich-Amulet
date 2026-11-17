"""Ring A - 5 mm flat band, pave row along one edge + 2-stone bar across the top.
From drawing: width 5.00, top thickness 1.87, bottom thickness 1.53,
stones: 1.10 x23, 1.50 x1, 2.00 x1.
Measured from the drawing (scale ~13.1 px/mm): inner dia 16.0,
pave strip 1.25 wide on one edge (stepped 0.30 below the band surface, prongs between stones),
pave covers the upper half (23 stones at 1.22 pitch, +-79.5 deg),
inner channel 2.0 wide x 0.60 deep under the pave side (inner step visible in the drawing; depth set so the 925 weight matches the table),
bar slot at top centre from the strip to 0.1 from the other edge; 2.00 stone next to the strip, 1.50 below it."""
import numpy as np, sys
from common import *

ID, W, T_TOP, T_BOT = 16.0, 5.00, 1.87, 1.53
STRIP, STEP = 1.25, 0.30
CH_W, CH_D = 2.0, 0.60      # inner channel under the pave side (step line visible inside the ring in the drawing)
N_PAVE, D_PAVE, PITCH = 23, 1.10, 1.22
ri = ID / 2
Rm = ri + (T_TOP + T_BOT) / 2          # outer circle radius
dz = (T_TOP - T_BOT) / 2               # outer circle shifted up -> top 1.87, bottom 1.53
y0 = -W / 2                            # pave edge
ys = y0 + STRIP

def R_out(t):
    return np.sqrt(Rm**2 - (dz * np.sin(t))**2) + dz * np.cos(t)

loops = []
for t in np.linspace(0, 2*np.pi, 721)[:-1]:
    R = R_out(t)
    sec = [(ri + CH_D, y0), (ri + CH_D, y0 + CH_W), (ri, y0 + CH_W), (ri, W/2), (R, W/2), (R, ys), (R - STEP, ys), (R - STEP, y0)]
    loops.append(ring_loop(sec, t))
metal = sweep(loops)

stones, cuts, adds = [], [], []
# ---- pave row ----
yc = y0 + STRIP / 2
Rs = R_out(0) - STEP
for i in range(N_PAVE):
    s = (i - (N_PAVE - 1) / 2) * PITCH
    t = s / Rs
    R = R_out(t) - STEP
    h = stone_height(D_PAVE)
    g = R - h + 0.08                     # table 0.08 proud of the strip, below band surface
    cuts.append(on_ring(seat(D_PAVE), np.degrees(t), g, yc))
    stones.append(on_ring(brilliant(D_PAVE), np.degrees(t), g, yc))
# shared claws between neighbouring stones on both strip edges + end claws
for i in range(N_PAVE + 1):
    s = (i - N_PAVE / 2) * PITCH
    t = s / Rs; R = R_out(t) - STEP
    for yy in (y0 + 0.24, ys - 0.17):
        adds.append(on_ring(Manifold.cylinder(0.25, 0.2, 0.2, 16) + Manifold.sphere(0.2, 16).translate([0, 0, 0.25]), np.degrees(t), R - 0.02, yy))

# ---- bar slot with 2.00 + 1.50 ----
R0 = R_out(0)
slot_top_w, slot_bot_w, slot_depth = 2.30, 1.60, 0.35
y_a, y_b = ys, W/2 - 0.10
slot = Manifold.hull_points([(x, y, z) for (x, y) in [(-slot_top_w/2, y_a), (slot_top_w/2, y_a), (-slot_bot_w/2, y_b), (slot_bot_w/2, y_b)]
                             for z in (R0 - slot_depth, R0 + 1)])
metal = metal - slot
for d, yy in ((2.00, y0 + 2.28), (1.50, y0 + 4.07)):
    g = R0 - slot_depth - 0.03 - 0.0 + 0.05 - 0.0
    g = R0 - slot_depth + 0.10            # girdle a little above the slot floor, table ~ band surface
    cuts.append(seat(d).translate([0, yy, g])); stones.append(brilliant(d).translate([0, yy, g]))
    for sx in (-1, 1):                     # two claws each side of every bar stone
        for sy in (-1, 1):
            px, py = sx * (d/2 + 0.05) * 0.72, yy + sy * (d/2) * 0.62
            adds.append(Manifold.cylinder(slot_depth + 0.25, 0.2, 0.17, 16).translate([px, py, R0 - slot_depth - 0.05])
                        + Manifold.sphere(0.19, 16).translate([px, py, R0 + 0.2]))

metal = (metal - union(cuts)) + union(adds)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    tm, _ = export("ring-A-pave-band", metal, stones, out)
    print("metal vol", round(tm.volume, 2), "watertight", tm.is_watertight, "bbox", np.round(tm.bounds, 2).tolist(), "stones", len(stones))
