#!/bin/sh
# Rebuild every ring, run the dimension check and render previews.  Usage: sh build_all.sh [outdir]
set -e
OUT=${1:-stl}
for r in ring_a_pave_band ring_b_twist ring_c_oval_solitaire ring_d_signet ring_e_jade_cabochon; do python3 $r.py "$OUT"; done
python3 check_dims.py
for n in ring-A-pave-band ring-B-twist ring-C-oval-solitaire ring-D-signet ring-E-jade-cabochon; do
  python3 render.py "$OUT/$n-metal.stl" "$OUT/$n-preview.png" "$OUT/$n-stones.stl"
done
python3 annotate.py
python3 export_3dm.py
