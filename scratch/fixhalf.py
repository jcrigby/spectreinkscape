import sys, math, re, subprocess; sys.path.insert(0,"scratch")
import addpiece as A
APPLY = len(sys.argv)>1
tree, el, solid, notch = A.load()
old=subprocess.run(["git","show","HEAD:spectre.svg"],capture_output=True,text=True).stdout
def parse(d):
    t=re.findall(r"[mlhvz]|-?\d+\.?\d*(?:e-?\d+)?",d,re.I); pts=[]; x=y=0; i=0; cmd=None
    while i<len(t):
        if t[i].isalpha(): cmd=t[i]; i+=1; continue
        if cmd in "mM lL".replace(" ",""):
            dx,dy=float(t[i]),float(t[i+1]); i+=2
            if cmd.islower() and pts: x+=dx;y+=dy
            elif cmd.islower(): x,y=dx,dy
            else: x,y=dx,dy
            if cmd=="m": cmd="l"
            if cmd=="M": cmd="L"
        elif cmd in "hH": v=float(t[i]); i+=1; x=x+v if cmd=="h" else v
        elif cmd in "vV": v=float(t[i]); i+=1; y=y+v if cmd=="v" else v
        pts.append((x,y))
    return pts
moved=[]
for e in list(el["play"]):
    i=e.get("id"); d=e.get("d")
    if i in ("movehex","movetri"): continue
    m=re.search(r'id="%s"[^>]*? d="([^"]+)"'%i, old)
    if m and m.group(1)==d: continue
    p=parse(d); assert len(p)==3,(i,d)
    off=560 if sum(q[0] for q in p)/3>640 else 0
    moved.append((i,[(q[0]-off,q[1]) for q in p]))
obst={**solid,**notch}
anch=[]
def addanch(poly):
    n=len(poly)
    for k in range(n):
        a,b=poly[k],poly[(k+1)%n]; anch.append(a)
        L=math.dist(a,b)
        if abs(L-50)<.1 or abs(L-86.6)<.1: anch.append(((a[0]+b[0])/2,(a[1]+b[1])/2))
for v in obst.values(): addanch(v)
done={}; pending=dict(moved)
for rnd in range(6):
    prog=False
    for i,p in list(pending.items()):
        best=None
        for v in p:
            for a in anch:
                dx,dy=a[0]-v[0],a[1]-v[1]; dist=math.hypot(dx,dy)
                if dist>7: continue
                q=[(x+dx,y+dy) for x,y in p]
                # exact shape rebuild: snap side lengths are already exact (user moved exact pieces)
                hits=sum(A.clip(q,o) for o in list(obst.values())+list(done.values()))
                if hits>.5 or A.clip(A.Q,q)<A.area(q)-.5: continue
                score=sum(min(math.dist(w,a2) for a2 in anch) for w in q)
                if best is None or (score,dist)<best[0]: best=((score,dist),q)
        if best:
            done[i]=best[1]; del pending[i]; addanch(best[1]); prog=True
            print(i,"moved %.1f px, snap score %.2f"%(best[0][1],best[0][0]),[tuple(round(x,1) for x in w) for w in best[1]])
    if not prog: break
for i,p in pending.items(): print("UNPLACED",i,[tuple(round(x,1) for x in w) for w in p])
h=A.solid_hex if 0 else None
c=solid['chex01']; xs=sorted(set(round(q[0],4) for q in c)); 
R=max(q[0] for q in c); T=min(c,key=lambda q:q[1])
done['path35']=[(R,T[1]),(R,T[1]+25),T]
if APPLY:
    for n,(i,q) in enumerate(done.items(),1):
        A.add(tree, el, solid, notch, "chalf%02d"%n, "#f08a1c", q)
        m=re.search(r'id="%s"[^>]*? d="([^"]+)"'%i, old)
        if m: el[i].set("d",m.group(1))
        else: el["play"].remove(el[i])
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
