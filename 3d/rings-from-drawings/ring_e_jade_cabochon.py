"""Ring E - men's jade cabochon ring, 4 bead-tip claws, bezel rim, pave shoulders ("design 4, classic luxury" photo).
Stone, from IGA report TG2506120063: natural jadeite, oval cabochon 18.18 x 24.90 x 10.50 mm, 48.90 ct.
Long axis along the finger (as in the photo: 18.18 across, 24.90 along the finger).
Proportions from the photo (scale = stone width 18.18 mm), checked against casting/CAD production
standards (bezel wall 0.45-0.7, prong >= 0.45, metal >= 1.2 under stone settings, open gaps >= 0.4):
  bezel wall 0.70, 1.60 high; 4 claws 1.30 thick, tips 1.60, holding the dome 3.4 mm above the base;
  shoulders flush with the bezel (ring 23 mm wide, not wider than the head), 22.0 long at the head,
  tapering to 5.50 under the finger; pave on the sloping shoulder faces, round 1.50 mm, 0.15 gaps;
  shoulders hollowed from inside (1.30 walls) and an open gallery under the stone, so the weight is realistic.
Ring size from the customer: Thai 58 = inner circumference 58 mm -> inner dia 58/pi = 18.46 (about US 8 1/4).
Assumed (not in photo/report):
bottom thickness 2.00, metal under the stone 2.00."""
import numpy as np, sys
from scipy.interpolate import PchipInterpolator
from manifold3d import CrossSection
from common import *

# ---------- numbers ----------
SA, SB, SH = 18.18, 24.90, 10.50          # stone width (X), length (Y, along finger), height
GIRDLE = 1.00                              # straight wall at the base of the cabochon
CT, SG = 48.90, 3.33                       # report weight, jadeite specific gravity
SIZE_TH = 58
ID, T_BOT, W_BOT, UNDER = SIZE_TH / np.pi, 2.00, 5.50, 2.00
RIM_T, RIM_H, CLR = 0.70, 1.60, 0.05
PAVE, WALL = 1.70, 1.30
ri = ID / 2
z0 = ri + UNDER                            # flat base of the stone
a, b = SA / 2, SB / 2

# ---------- cabochon: dome z = Hd * (1 - rho^2)^p, p fitted so the volume gives 48.90 ct ----------
Hd = SH - GIRDLE
area = np.pi * a * b
want = CT * 0.2 / SG * 1000                # mm3
p = area * Hd / (want - area * GIRDLE) - 1
def cabochon():
    rho = np.r_[np.linspace(0, 0.9, 30), 1 - np.geomspace(0.1, 1e-4, 40)]
    prof = [(0, 0), (1, 0), (1, GIRDLE)] + [(r, GIRDLE + Hd * (1 - r * r) ** p) for r in rho[::-1]]
    prof = [(x, y) for x, y in prof if not (x == 0 and y == GIRDLE + Hd and False)]
    return Manifold.revolve(CrossSection([prof]), 160).scale([a, b, 1])
def stone_z(x, y):
    r2 = (x / a) ** 2 + (y / b) ** 2
    return z0 + GIRDLE + Hd * max(0.0, 1 - r2) ** p if r2 <= 1 else z0
stone = cabochon().translate([0, 0, z0])

# ---------- shank: sweep, flat platform at the stone base ----------
# shoulder outline in the front view, flush with the bezel foot (x = a + rim), easing into the band.
# points (x, z) relative to the stone base -> (angle, radius) so it follows any ring size
XH = a + CLR + RIM_T
SH_PTS = [(XH, z0), (XH + 1.40, z0 - 4.6), (XH + 1.70, z0 - 9.0)]
sh_deg = [float(np.degrees(np.arctan2(x, z))) for x, z in SH_PTS]
sh_R = [float(np.hypot(x, z)) for x, z in SH_PTS]
deg = [0] + sh_deg + [100, 130, 180]
Rk = PchipInterpolator(deg, [sh_R[0] + 1.15] + sh_R + [ri + 2.50, ri + 2.15, ri + T_BOT])
Wk = PchipInterpolator(deg, [22.0, 22.0, 18.0, 12.5, 8.5, 6.4, W_BOT])
def ang(t): return abs(np.degrees(np.arctan2(np.sin(t), np.cos(t))))
CH = 0.6
def section(t):
    A = ang(t); R = float(Rk(A)); w = float(Wk(A)) / 2; wi = w - 0.35
    return [(ri - 0.1, -wi), (ri - 0.1, wi), (R - CH, w), (R, w - CH), (R, -w + CH), (R - CH, -w)]
shank = sweep([ring_loop(section(t), t) for t in np.linspace(0, 2 * np.pi, 721)[:-1]])
shank = shank - Manifold.cube([80, 80, 40]).translate([-40, -40, z0])          # platform at z0

# ---------- head: oval cup + bezel rim ----------
def oval_prism(ra, rb, zlo, zhi, n=160):
    return Manifold.cylinder(zhi - zlo, 1, 1, n).scale([ra, rb, 1]).translate([0, 0, zlo])
head = oval_prism(a + CLR + RIM_T, b + CLR + RIM_T, z0 - 2.0, z0 + RIM_H)
metal = shank + head
metal = metal - oval_prism(a + CLR, b + CLR, z0, z0 + 20)                       # stone seat
metal = metal - oval_prism(a - 1.4, b - 1.4, 4.0, z0 + 1)                       # open gallery, 1.4 ledge
metal = metal - Manifold.cylinder(60, ri, ri, 256).rotate([90, 0, 0]).translate([0, 30, 0])  # finger hole

# ---------- back-cut: hollow the shoulders from the finger side, leaving WALL all round ----------
def pocket(side):
    loops = []
    for A in np.linspace(26.3, 117.7, 91):
        e = min(1.0, (A - 26.3) / 8, (117.7 - A) / 12)                # ease the pocket in and out
        R = float(Rk(A)); w = float(Wk(A)) / 2
        ro = ri + (R - WALL - ri) * e if e > 0 else ri - 0.2
        wy = max(0.3, (w - WALL) * min(1, e * 1.5))
        ro = max(ro, ri - 0.2)
        sec = [(ri - 1.0, -wy), (ri - 1.0, wy), (ro, wy), (ro, -wy)]
        loops.append(ring_loop(sec, side * np.radians(A))[::side])
    return sweep(loops, closed=False)
metal = metal - pocket(1) - pocket(-1)

# ---------- claws at the four corners ----------
def ell(phi, off):
    e = np.array([a * np.cos(phi), b * np.sin(phi)]); n = np.array([np.cos(phi) / a, np.sin(phi) / b])
    n /= np.linalg.norm(n); return e + n * off
def tube(pts, r0, r1):
    rs = np.linspace(r0, r1, len(pts)); sph = [Manifold.sphere(r, 20).translate(q) for q, r in zip(pts, rs)]
    return union([Manifold.batch_hull([u, v]) for u, v in zip(sph[:-1], sph[1:])])
CLAW_PHI = [np.radians(d) for d in (52, 128, 232, 308)]
claws = []
for phi in CLAW_PHI:
    path = []
    # tip presses on the dome 3.4 mm above the stone base, just past the steep flank
    TZ = z0 + 3.4; off = 0.0
    while stone_z(*ell(phi, off - 0.02)) < TZ: off -= 0.02
    tx, ty = ell(phi, off + 0.45); tz = TZ + 0.15
    for off_, dz in [(0.70 + CLR, -0.8), (0.75 + CLR, RIM_H)]:
        x, y = ell(phi, off_); path.append((x, y, z0 + dz))
    path.append((tx, ty, tz))
    claws.append(tube(path, 0.65, 0.65) + Manifold.sphere(0.80, 24).scale([1, 1, 0.85]).translate([tx, ty, tz]))
metal = metal + union(claws)
metal = metal - Manifold.cylinder(60, ri, ri, 256).rotate([90, 0, 0]).translate([0, 30, 0])

# ---------- pave panels on both shoulders ----------
stones = [stone]
PITCH = PAVE + 0.15
gem = brilliant(PAVE); gh = stone_height(PAVE)
cut_list, gems, beads = [], [], []
for side in (1, -1):
    A = sh_deg[0] + 5.5
    while A <= sh_deg[2] - 4.0:
        R = float(Rk(A)); w = float(Wk(A)) / 2 - CH - 1.40
        n = int(np.floor(2 * w / PITCH)) + 1
        ys = (np.arange(n) - (n - 1) / 2) * PITCH
        for y in ys:
            t = side * A
            gems.append(on_ring(gem, t, R - gh + 0.05, y))
            cut_list.append(on_ring(seat(PAVE), t, R - gh + 0.05, y))
        for y in (ys[:-1] + ys[1:]) / 2:
            Ab = A + np.degrees(PITCH / 2 / R)
            beads.append(on_ring(Manifold.sphere(0.35, 12), side * Ab, float(Rk(Ab)) - 0.10, y))
        A += np.degrees(PITCH / R)
metal = metal - union(cut_list)
metal = metal + union(beads)
stones += gems
N_PAVE = len(gems)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    metal = metal.simplify(0.002); stones = [s_.simplify(0.002) for s_ in stones]
    tm, _ = export("ring-E-jade-cabochon", metal, stones, out)
    # drop zero-area slivers left by the boolean ops so the STL checks as one watertight body
    import trimesh
    for part in ("metal", "full", "stones"):
        f = f"{out}/ring-E-jade-cabochon-{part}.stl"; m = trimesh.load(f)
        m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices(); m.merge_vertices(); m.fill_holes()
        bodies = [q for q in m.split(only_watertight=False) if q.area > 1e-3]
        m = trimesh.util.concatenate(bodies); m.export(f)
        if part == "metal": tm = m
    sv = stone.volume()
    print(f"dome exponent p={p:.3f}; stone vol {sv:.0f} mm3 -> {sv*SG/1000/0.2:.2f} ct (report {CT})")
    print("pave stones", N_PAVE, "metal vol", round(tm.volume, 1), "watertight", tm.is_watertight,
          "silver925 g", round(tm.volume * 10.36 / 1000, 2), "bbox", np.round(tm.bounds, 2).tolist())
