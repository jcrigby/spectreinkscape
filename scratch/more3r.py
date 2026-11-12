import sys, math; sys.path.insert(0,"scratch")
import addpiece as A, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, signal
tree, el, solid, notch = A.load()
S=4; W,H=650*S,500*S
def rast(polys,shrink=0):
    im=Image.new("1",(W,H),0); d=ImageDraw.Draw(im)
    for p in polys: d.polygon([(x*S,y*S) for x,y in p],fill=1)
    return np.array(im,dtype=bool)
free=rast([A.Q]) & ~rast(list(solid.values())+list(notch.values()))
free=ndimage.binary_dilation(free,iterations=2)  # 0.5 px tolerance for touching edges
print("free px^2 ~", free.sum()/S/S)
lab,nl=ndimage.label(ndimage.binary_erosion(free,iterations=6))
for i in range(1,nl+1):
    ys,xs=np.nonzero(lab==i); print(" region",i,"area ~%.0f"%(len(xs)/S/S),"centre (%.0f,%.0f)"%(xs.mean()/S,ys.mean()/S), "bbox x %.0f-%.0f y %.0f-%.0f"%(xs.min()/S,xs.max()/S,ys.min()/S,ys.max()/S))
def reg(n,rot,R=50): return [(R*math.cos(math.radians(rot+360*j/n)), R*math.sin(math.radians(rot+360*j/n))) for j in range(n)]
shapes=[("hex",r,reg(6,r)) for r in range(0,60,5)]+[("trunc",r,reg(6,r)[:5]) for r in range(0,360,5)]+[("tri",r,reg(3,r,50/math.sqrt(3))) for r in range(0,120,5)]
res={}
for name,rot,sh in shapes:
    K=60*S*2+1; im=Image.new("1",(K,K),0); ImageDraw.Draw(im).polygon([((x+60)*S,(y+60)*S) for x,y in sh],fill=1); k=np.array(im,dtype=np.float32)
    bad=signal.fftconvolve((~free).astype(np.float32),k[::-1,::-1],mode="same")
    ok=bad<0.5
    n=ok.sum()
    if n:
        lab,nl=ndimage.label(ok); 
        spots=[(round(xs.mean()/S,1),round(ys.mean()/S,1),len(xs)) for ys,xs in (np.nonzero(lab==i) for i in range(1,nl+1))]
        print(name,rot,"fits at",spots)
        res[(name,rot)]=ok
print("---- can two triangles share the left pocket?")
def pts(key):
    ys,xs=np.nonzero(res[key]); return [(x/S,y/S) for x,y in zip(xs,ys) if x/S<400]
P={k:pts(k) for k in res if k[0]=="tri"}
best=(1e9,)
keys=[k for k in P if P[k]]
for i,a in enumerate(keys):
    for b in keys[i:]:
        sa=reg(3,a[1],50/math.sqrt(3)); sb=reg(3,b[1],50/math.sqrt(3))
        for pa in P[a][::7]:
            for pb in P[b][::7]:
                if math.dist(pa,pb)<20: continue
                o=A.clip([(x+pa[0],y+pa[1]) for x,y in sa],[(x+pb[0],y+pb[1]) for x,y in sb])
                if o<best[0]: best=(o,a,pa,b,pb)
print("smallest overlap between two triangles in the pocket:",best)
