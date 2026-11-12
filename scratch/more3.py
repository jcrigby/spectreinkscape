import sys, math, itertools, json; sys.path.insert(0,"scratch")
import addpiece as A
tree, el, solid, notch = A.load()
obst={**solid,**notch}
tileA=A.area(A.Q)
inner_cov=sum(A.clip(A.Q,v) for v in solid.values())
print("tile %.0f, covered inside straight outline %.0f, notches %.0f" % (tileA, inner_cov, sum(A.area(v) for v in notch.values())))
free=tileA-inner_cov-sum(A.clip(A.Q,v) for v in notch.values())
print("free interior area %.0f" % free)
def reg(n,rot,R=50): return [(R*math.cos(math.radians(rot+360*j/n)), R*math.sin(math.radians(rot+360*j/n))) for j in range(n)]
shapes=[]
for rot in (0,30): shapes.append(("hex",reg(6,rot)))
for rot in range(0,360,30): shapes.append(("trunc",reg(6,rot)[:5]))
for rot in (0,30,60,90): shapes.append(("tri",reg(3,rot,50/math.sqrt(3))))
anch=set()
for v in list(obst.values())+[A.Q]:
    for p in v: anch.add((round(p[0],2),round(p[1],2)))
cands={}
seen=set()
for gen in range(3):
    new=0
    for name,sh in shapes:
        for v in sh:
            for a in list(anch):
                poly=[(p[0]-v[0]+a[0],p[1]-v[1]+a[1]) for p in sh]
                key=(name,tuple(sorted((round(p[0],1),round(p[1],1)) for p in poly)))
                if key in seen: continue
                seen.add(key)
                if A.clip(A.Q,poly)<A.area(poly)-.5: continue
                if any(A.clip(poly,o)>.5 for o in obst.values()): continue
                cands[key]=poly; new+=1
    print("gen",gen,"new candidates",new,"total",len(cands))
    if not new: break
    for poly in cands.values():
        for p in poly: anch.add((round(p[0],2),round(p[1],2)))
keys=list(cands); polys=[cands[k] for k in keys]; ar=[A.area(p) for p in polys]; n=len(keys)
from collections import Counter; print(Counter(k[0] for k in keys))
conf=[set() for _ in range(n)]
for i in range(n):
    for j in range(i+1,n):
        if A.clip(polys[i],polys[j])>.5: conf[i].add(j); conf[j].add(i)
best=[0,[]]
order=sorted(range(n),key=lambda i:-ar[i])
import time; t0=time.time()
def bb(idx,avail,cur,chosen):
    if time.time()-t0>240: return
    if cur>best[0]: best[0]=cur; best[1]=chosen[:]
    rem=[i for i in idx if i in avail]
    if cur+min(sum(ar[i] for i in rem), free-cur+1)<=best[0]+1: return
    if not rem: return
    i=max(rem,key=lambda i:(ar[i],-len(conf[i]&avail)))
    chosen.append(i); bb(rem,avail-conf[i]-{i},cur+ar[i],chosen); chosen.pop()
    bb(rem,avail-{i},cur,chosen)
sys.setrecursionlimit(100000)
bb(order,set(range(n)),0,[])
print("best extra area %.0f of free %.0f (%.1f%%), time %.0fs" % (best[0],free,100*best[0]/free,time.time()-t0))
for i in best[1]: print(keys[i][0],[tuple(round(x,1) for x in p) for p in polys[i]])
json.dump([(keys[i][0],polys[i]) for i in best[1]],open("scratch/more3.json","w"))
