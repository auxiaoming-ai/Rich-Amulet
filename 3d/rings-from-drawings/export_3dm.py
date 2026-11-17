"""Write every ring as a Rhino 8 .3dm file (millimetres) with named, coloured layers:
Metal / Jade / Diamonds (or Stones) / Dimensions. The dimension geometry is the same 3D text and arrows as the
-spec files. The spec numbers are also stored as Attribute User Text on the metal object
(Rhino: select the metal, Properties panel > Attribute User Text). Meshes only: rhino3dm cannot make NURBS booleans; use
Rhino's MeshToNURB / QuadRemesh + ToSubD if editable surfaces are needed."""
import numpy as np, trimesh, rhino3dm as r

def rmesh(tm):
    m = r.Mesh()
    for v in tm.vertices: m.Vertices.Add(float(v[0]), float(v[1]), float(v[2]))
    for f in tm.faces: m.Faces.AddFace(int(f[0]), int(f[1]), int(f[2]))
    m.Normals.ComputeNormals(); m.Compact()
    return m

def add_layer(model, name, rgb, gloss=0.6, transp=0.0):
    mat = r.Material(); mat.Name = name; mat.DiffuseColor = (*rgb, 255)
    mat.Reflectivity = gloss; mat.Transparency = transp
    mi = model.Materials.Add(mat)
    L = r.Layer(); L.Name = name; L.Color = (*rgb, 255); L.RenderMaterialIndex = mi
    return model.Layers.Add(L)

def add(model, tm, layer, name, user_text=None):
    at = r.ObjectAttributes(); at.LayerIndex = layer; at.Name = name
    for k, v in (user_text or {}).items(): at.SetUserString(k, v)
    model.Objects.AddMesh(rmesh(tm), at)

def write(name, title, user_text, jade=False):
    model = r.File3dm(); model.Settings.ModelUnitSystem = r.UnitSystem.Millimeters
    metal = trimesh.load(f"stl/{name}-metal.stl")
    lm = add_layer(model, "Metal", (200, 200, 205), 0.9)
    add(model, metal, lm, f"{title} metal", user_text)
    st = trimesh.load(f"stl/{name}-stones.stl").split(only_watertight=False)
    st = sorted(st, key=lambda s: -s.volume)
    if jade:
        lj = add_layer(model, "Jade", (20, 140, 70), 0.5, 0.15); add(model, st[0], lj, "Jadeite cabochon")
        st = st[1:]
    ld = add_layer(model, "Diamonds" if jade else "Stones", (235, 245, 255), 0.95, 0.3)
    add(model, trimesh.util.concatenate(st), ld, f"{len(st)} stones")
    sc = trimesh.load(f"stl/{name}-spec.3mf")
    dims = [g for k, g in sc.geometry.items() if "dimension" in k]
    if dims:
        lx = add_layer(model, "Dimensions", (30, 120, 230), 0.1)
        add(model, trimesh.util.concatenate(dims), lx, "dimensions and spec text")
    model.Write(f"stl/{name}.3dm", 8)
    print(name, "->", f"stl/{name}.3dm")

if __name__ == "__main__":
    E = trimesh.load("stl/ring-E-jade-cabochon-metal.stl").volume
    write("ring-E-jade-cabochon", "Ring E", {
        "Stone": "Natural jadeite oval cabochon 24.90 x 18.18 x 10.50 mm, 48.90 ct (IGA TG2506120063)",
        "Ring size": "Thai 58 = inner circumference 58 mm, inner dia 18.46 mm (US 8 1/4)",
        "Setting": "Bezel wall 0.70 x 1.60 high, 4 claws 1.30 mm, open gallery with 1.40 ledge",
        "Shank": "Shoulders 22.0 long, band bottom 5.50 wide x 2.00 thick, hollow back walls 1.30",
        "Pave": "Round 1.70 mm (sieve 2 fen) x 66, 33 per side",
        "Metal volume mm3": f"{E:.1f}",
        "Weight silver 925 g": f"{E * 10.36 / 1000:.2f}",
        "Weight gold 18K g": f"{E * 10.36 * 1.4 / 1000:.2f}",
    }, jade=True)
    for n, t in (("ring-A-pave-band", "Ring A"), ("ring-B-twist", "Ring B"),
                 ("ring-C-oval-solitaire", "Ring C"), ("ring-D-signet", "Ring D")):
        write(n, t, {"Source": "Chinese technical drawing, dimensions per drawing (see README)"})
