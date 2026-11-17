import trimesh, numpy as np, matplotlib, sys; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
def r1(metal, stones, out, el, az, color=(0.9,0.62,0.48), lim=None, size=7, center=(0,0,0)):
    parts=[(trimesh.load(metal),color)]
    if stones: parts.append((trimesh.load(stones),(0.85,0.92,1.0)))
    m=parts[0][0]; ext=lim or np.abs(m.bounds).max()*1.02
    fig=plt.figure(figsize=(size,size),facecolor="#00302e"); ax=fig.add_subplot(111,projection='3d',proj_type='ortho'); ax.set_facecolor("#00302e")
    e,a=np.radians(el),np.radians(az); v=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
    L=v*0.5+np.array([0.3,-0.3,0.8]); L/=np.linalg.norm(L)
    tris=[];cols=[]
    for mm,c in parts:
        sh=np.clip(mm.face_normals@L,0,1)**1.5*0.8+0.2
        tris.append(mm.vertices[mm.faces]); cols.append(np.c_[np.clip(np.outer(sh,c),0,1),np.ones(len(sh))])
    ax.add_collection3d(Poly3DCollection(np.vstack(tris),facecolors=np.vstack(cols),edgecolors='none'))
    cx,cy,cz=center
    ax.set_xlim(cx-ext,cx+ext);ax.set_ylim(cy-ext,cy+ext);ax.set_zlim(cz-ext,cz+ext);ax.set_box_aspect((1,1,1));ax.view_init(el,az);ax.axis('off')
    plt.subplots_adjust(0,0,1,1); plt.savefig(out,dpi=70,facecolor=fig.get_facecolor()); plt.close()
if __name__=="__main__":
    a=sys.argv; c=tuple(map(float,a[7].split(','))) if len(a)>7 else (0,0,0)
    r1(a[1], a[2] if a[2]!='-' else None, a[3], float(a[4]), float(a[5]), lim=float(a[6]) if len(a)>6 else None, center=c)
