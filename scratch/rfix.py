"""Helpers for fixing hand edits on the right tile (tileR). Coordinates are tile-local (left-tile) coords."""
import sys, math, re, xml.etree.ElementTree as ET
sys.path.insert(0,"scratch")
import addpiece as A
SVG=A.SVG; W=100/9; PREV="scratch/prev.svg"
t=ET.parse("spectre.svg"); r=t.getroot(); el={e.get("id"):e for e in r.iter() if e.get("id")}
par={c:p for p in r.iter() for c in p}
import os
prev={e.get("id"):e for e in ET.parse(PREV).getroot().iter() if e.get("id")} if os.path.exists(PREV) else {}   # PREV: git show HEAD:spectre.svg > scratch/prev.svg
def parse(d):
    tk=re.findall(r"[mlhvzMLHVZ]|-?\d+\.?\d*(?:e-?\d+)?",d); pts=[]; x=y=0.0; i=0; cmd=None
    while i<len(tk):
        if tk[i].isalpha(): cmd=tk[i]; i+=1; continue
        if cmd in "mMlL":
            a,b=float(tk[i]),float(tk[i+1]); i+=2
            if cmd.islower() and pts: x+=a; y+=b
            else: x,y=a,b
            cmd="l" if cmd=="m" else "L" if cmd=="M" else cmd
        elif cmd in "hH": v=float(tk[i]); i+=1; x=x+v if cmd=="h" else v
        elif cmd in "vV": v=float(tk[i]); i+=1; y=y+v if cmd=="v" else v
        else: raise ValueError(d)
        pts.append((x,y))
    return pts
def D(poly): return "M "+" L ".join("%.4f %.4f"%p for p in poly)+" Z"
def pat_of(name):
    p=el.get(name+"pat_r"); return p if p is not None else el.get(name+"_rpat")
def poly_of(name): return parse(el[name+"_r"].get("d"))
def setpiece(name,poly):
    g=el["pc_"+name+"_r"]; g.attrib.pop("transform",None)
    for i in (name+"bg_r",name+"_r"): el[i].set("d",D(poly))
    n=len(poly); cc=(sum(p[0] for p in poly)/n,sum(p[1] for p in poly)/n)
    pat=pat_of(name); m=re.search(r"rotate\(([-\d.]+)\)",pat.get("patternTransform"))
    pat.set("patternTransform","translate(%.4f %.4f) rotate(%s) translate(%.5f 0)"%(*cc,m.group(1),-W/2))
def shift(name,dx,dy): setpiece(name,[(x+dx,y+dy) for x,y in poly_of(name)])
def delpiece(name):
    g=el["pc_"+name+"_r"]; par[g].remove(g); p=pat_of(name); par[p].remove(p)
def newpiece(name,poly,col):
    th=math.degrees(math.atan2(poly[1][1]-poly[0][1],poly[1][0]-poly[0][0]))%180
    n=len(poly); cc=(sum(p[0] for p in poly)/n,sum(p[1] for p in poly)/n)
    pat=ET.SubElement(el["centre_defs_r"],SVG+"pattern",{"id":name+"pat_r","patternUnits":"userSpaceOnUse","width":"%.5f"%(2*W),"height":"%.5f"%(2*W),"patternTransform":"translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)"%(*cc,th,-W/2)})
    ET.SubElement(pat,SVG+"rect",{"x":"0","y":"0","width":"%.5f"%W,"height":"%.5f"%(2*W),"style":"fill:%s;stroke:none"%col})
    g=ET.SubElement(el["centre_r"],SVG+"g",{"id":"pc_"+name+"_r"})
    ET.SubElement(g,SVG+"path",{"id":name+"bg_r","d":D(poly),"style":"fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round"%col})
    ET.SubElement(g,SVG+"path",{"id":name+"_r","d":D(poly),"style":"fill:url(#%spat_r);stroke:none"%name})
    el["pc_"+name+"_r"]=g; el[name+"_r"]=g[1]; el[name+"bg_r"]=g[0]; el[name+"pat_r"]=pat
def repark(i): el[i].set("d",prev[i].get("d")); el[i].attrib.pop("transform",None)
def finish():
    pieces={g.get("id"):parse(g[0].get("d")) for g in el["tileR"].iter() if (g.get("id") or "").startswith("pc_")}
    for g in el["tileR"].iter(): assert not ((g.get("id") or "").startswith("pc_") and g.get("transform")), g.get("id")
    notch={"notch %d"%k:A.nums(el["hex%02din_r"%(k-1)].get("d")) for k in range(2,15,2)}
    names=list(pieces); bad=[]
    for i,x in enumerate(names):
        for o,v in notch.items():
            if A.clip(pieces[x],v)>.5: bad.append((x,o,round(A.clip(pieces[x],v),1)))
        for y in names[i+1:]:
            ov=A.clip(pieces[x],pieces[y])
            if ov>.5: bad.append((x,y,round(ov,1)))
    print("overlaps:",bad); assert not bad
    from collections import Counter
    print(len(pieces),"pieces", dict(Counter(len(v) for v in pieces.values())), "coverage %.1f%%"%(100*sum(A.area(v) for v in pieces.values())/A.area(A.Q)))
    ids=[e.get("id") for e in r.iter() if e.get("id")]; assert len(ids)==len(set(ids))
    t.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
