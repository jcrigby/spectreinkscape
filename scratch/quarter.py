import sys, math, json, time; sys.path.insert(0,"scratch")
import rfix as F
A=F.A; el=F.el
pieces={g.get("id"):F.parse(g[0].get("d")) for g in el["tileR"].iter() if (g.get("id") or "").startswith("pc_")}
notch={"notch %d"%k:F.parse(el["hex%02din_r"%(k-1)].get("d")) for k in range(2,15,2)}
obst={**pieces,**notch}
inner=sum(A.clip(A.Q,v) for v in pieces.values()); free=A.area(A.Q)-inner-sum(A.clip(A.Q,v) for v in notch.values())
print("free interior area %.0f px2"%free)
h=25*math.sqrt(3)
TRI=[(0,0),(12.5,0),(0,-h/2)]                 # top half: 30-60-90, legs 12.5 and 21.65, hyp 25
TRAP=[(0,0),(25,0),(12.5,-h/2),(0,-h/2)]      # bottom half: parallel 25 and 12.5, height 21.65, slant 25
print("tri area %.1f, trap area %.1f"%(A.area(TRI),A.area(TRAP)))
shapes=[]
for name,base in (("trap",TRAP),("tri",TRI)):
    for flip in (1,-1):
        for rot in range(0,360,30):
            a=math.radians(rot); shapes.append((name,[(flip*x*math.cos(a)-y*math.sin(a), flip*x*math.sin(a)+y*math.cos(a)) for x,y in base]))
anch=set()
def addanch(poly):
    n=len(poly)
    for k in range(n):
        a,b=poly[k],poly[(k+1)%n]; anch.add((round(a[0],2),round(a[1],2))); anch.add((round((a[0]+b[0])/2,2),round((a[1]+b[1])/2,2)))
for v in obst.values(): addanch(v)
addanch(A.Q)
# only anchors near free space matter: keep all, cheap bbox reject below
ob=[(v,min(p[0] for p in v),max(p[0] for p in v),min(p[1] for p in v),max(p[1] for p in v)) for v in obst.values()]
def clear(poly):
    if A.clip(A.Q,poly)<A.area(poly)-.3: return False
    x0=min(p[0] for p in poly);x1=max(p[0] for p in poly);y0=min(p[1] for p in poly);y1=max(p[1] for p in poly)
    for v,a,b,c,d in ob:
        if b<x0 or a>x1 or d<y0 or c>y1: continue
        if A.clip(poly,v)>.3: return False
    return True
cands={}; seen=set()
for gen in range(3):
    new=0
    for name,sh in shapes:
        for v in sh:
            for a in list(anch):
                poly=[(p[0]-v[0]+a[0],p[1]-v[1]+a[1]) for p in sh]
                key=(name,tuple(sorted((round(p[0],1),round(p[1],1)) for p in poly)))
                if key in seen: continue
                seen.add(key)
                if clear(poly): cands[key]=poly; new+=1
    print("gen",gen,"new",new,"total",len(cands)); 
    if not new: break
    for poly in list(cands.values()): addanch(poly)
keys=list(cands); polys=[cands[k] for k in keys]; ar=[A.area(p) for p in polys]; n=len(keys)
from collections import Counter; print(Counter(k[0] for k in keys))
conf=[set() for _ in range(n)]
bb=[(min(p[0] for p in v),max(p[0] for p in v),min(p[1] for p in v),max(p[1] for p in v)) for v in polys]
for i in range(n):
    for j in range(i+1,n):
        if bb[i][1]<bb[j][0] or bb[i][0]>bb[j][1] or bb[i][3]<bb[j][2] or bb[i][2]>bb[j][3]: continue
        if A.clip(polys[i],polys[j])>.3: conf[i].add(j); conf[j].add(i)
# components, then exact branch and bound per component (time-capped), greedy fallback
comp=[-1]*n; comps=[]
for i in range(n):
    if comp[i]>=0: continue
    st=[i]; comp[i]=len(comps); cur=[]
    while st:
        u=st.pop(); cur.append(u)
        for w in conf[u]:
            if comp[w]<0: comp[w]=len(comps); st.append(w)
    comps.append(cur)
sys.setrecursionlimit(100000); chosen=[]
for cur in comps:
    best=[0,[]]; t0=time.time()
    def rec(avail,val,pick):
        if val>best[0]: best[0]=val; best[1]=pick[:]
        if not avail or time.time()-t0>20: return
        if val+sum(ar[i] for i in avail)<=best[0]+1e-6: return
        i=max(avail,key=lambda i:(ar[i],-len(conf[i]&avail)))
        pick.append(i); rec(avail-conf[i]-{i},val+ar[i],pick); pick.pop()
        rec(avail-{i},val,pick)
    rec(set(cur),0,[])
    chosen+=best[1]
tot=sum(ar[i] for i in chosen)
print("components",len(comps),"| chosen",Counter(keys[i][0] for i in chosen),"| extra area %.0f of free %.0f (%.0f%%)"%(tot,free,100*tot/free))
print("coverage %.1f%% -> %.1f%%"%(100*sum(A.area(v) for v in pieces.values())/A.area(A.Q),100*(sum(A.area(v) for v in pieces.values())+tot)/A.area(A.Q)))
json.dump([(keys[i][0],polys[i]) for i in chosen],open("scratch/quarter.json","w"))
