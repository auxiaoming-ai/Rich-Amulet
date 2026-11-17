"""Render front / top / side / 3-4 views of an STL (orthographic) for checking against the drawing."""
import trimesh, numpy as np, matplotlib, sys; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def render(path, out, color=(0.85,0.62,0.45), stones=None):
    m = trimesh.load(path); parts=[(m,color)]
    if stones: parts.append((trimesh.load(stones),(0.92,0.95,1.0)))
    ext = max(np.abs(m.bounds).max(), 1) * 1.05
    fig = plt.figure(figsize=(16,4.6), facecolor="#00302e")
    views=[(0,-90,"front (along finger)"),(90,-90,"top"),(0,0,"side"),(25,-60,"3/4")]
    for i,(el,az,t) in enumerate(views):
        ax = fig.add_subplot(1,4,i+1, projection="3d", proj_type="ortho"); ax.set_facecolor("#00302e")
        e,a=np.radians(el),np.radians(az); v=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
        L=v*0.55+np.array([0.35,-0.25,0.75]); L/=np.linalg.norm(L)
        tris=[];cols=[]
        for mm,c in parts:
            n=mm.face_normals; sh=np.clip(n@L,0,1)*0.7+0.3
            tris.append(mm.vertices[mm.faces]); cols.append(np.c_[np.clip(np.outer(sh,c),0,1),np.ones(len(sh))])
        ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors="none"))
        ax.set_xlim(-ext,ext);ax.set_ylim(-ext,ext);ax.set_zlim(-ext,ext); ax.set_box_aspect((1,1,1))
        ax.view_init(el,az); ax.axis("off"); ax.set_title(t,color="w")
    plt.tight_layout(); plt.savefig(out,dpi=80,facecolor=fig.get_facecolor()); plt.close()
if __name__=="__main__":
    render(sys.argv[1], sys.argv[2], stones=sys.argv[3] if len(sys.argv)>3 else None)
