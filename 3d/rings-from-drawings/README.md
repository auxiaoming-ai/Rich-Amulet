# Rings built from the four technical drawings

Run `sh build_all.sh` to rebuild everything into `stl/`. It needs Python with `manifold3d trimesh scipy rtree matplotlib`.
Units are mm. The finger axis is Y and the top of the ring is +Z.

Each ring has these files in `stl/`:
- `*-full.stl`: metal and stones together
- `*-metal.stl`: metal only (for casting or printing)
- `*-stones.stl`: stones only
- `*.3mf`: metal and stones as separate objects in one file
- `*-preview.png`: rendered preview

## Dimensions taken from the drawings
`check_dims.py` measures every finished mesh against these numbers. The model differs from every dimension below by 0.00 mm.

| Ring | Dimensions on the drawing | Stones |
|---|---|---|
| A pave band | width 5.00, top thickness 1.87, bottom thickness 1.53 | 1.10 ×23, 1.50 ×1, 2.00 ×1 |
| B twist | top width 3.20, bottom width 2.42, top thickness 2.39, bottom thickness 1.62 | 1.10/1.30/1.50/1.70 ×2 each, 1.80 ×4 |
| C oval solitaire | 7.61 from table to finger hole, bottom thickness 1.62, bottom width 2.17 | oval 9.50×7.50, 1.10 ×14, 1.00 ×14 |
| D signet | inner diameter 18.42, top thickness 2.26, bottom thickness 1.54, top width 3.38, bottom width 2.37 | 2.31 ×1 |

## Values measured from the drawing scale (not printed on the drawing)
- **Inner diameter of A, B and C.** These are measured off the drawings using each drawing's own printed dimensions as the scale: A 16.0, B 16.0, C 16.5. Change `ID` at the top of each script.
- **Feature positions.** These are measured the same way: pave extent, stone positions, ribbon angle on B, claw angles and hidden-halo size on C, flat-top length 13.6 and stone offset 4.2 on D. Each script lists them in its header.

## Weight check (silver 925 at 10.36 g/cm³)
| Ring | Model | Drawing | Difference |
|---|---|---|---|
| A | 3.886 g | 3.802 g | +2.2 % |
| B | 2.593 g | 2.561 g | +1.2 % |
| C | 2.652 g | 2.628 g | +0.9 % |
| D | 3.412 g | 2.557 g | +33 % |

Ring D matches every printed dimension but is heavier than the drawing's weight table. The original probably has hollowing or thinner sections that the drawing views do not show.
