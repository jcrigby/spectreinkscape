"""Regenerate the tiling patch from the right tile and make the left tile a locked copy of it."""
import sys, copy, re, math; sys.path.insert(0,"scratch")
import rfix as F, xml.etree.ElementTree as ET
from collections import Counter
el,r=F.el,F.r; SVG=F.SVG
INK="{http://www.inkscape.org/namespaces/inkscape}"; SODI="{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}"
R=el["tileR"]
pieces=[F.parse(g[0].get("d")) for g in R.iter() if (g.get("id") or "").startswith("pc_")]
for g in R.iter(): assert not ((g.get("id") or "").startswith("pc_") and g.get("transform")), g.get("id")
g=el["patchtile"]; outline_d=el["patchtile_outline"].get("d")
for c in list(g): g.remove(c)
ET.SubElement(g,SVG+"path",{"id":"patchtile_outline","d":outline_d})
unit=lambda p:((p[0]-200)/100,(350-p[1])/100); cnt=Counter()
KINDS={(50.0,50.0,50.0):("tri","#4a7fe0"),(25.0,43.3,50.0):("half","#f5a03a"),(12.5,21.7,25.0):("qtri","#12a5a8"),(12.5,21.7,25.0,25.0):("trap","#9b59d0")}
for n,poly in enumerate(pieces):
    s=tuple(sorted(round(math.dist(poly[i],poly[(i+1)%len(poly)]),1) for i in range(len(poly))))
    kind,col=KINDS[s]; cnt[kind]+=1
    ET.SubElement(g,SVG+"path",{"id":"patchpiece%02d"%n,"d":"M "+" L ".join("%.5f %.5f"%unit(p) for p in poly)+" Z","style":"fill:%s;stroke:#ffffff;stroke-width:0.02;stroke-linejoin:round"%col})
ET.SubElement(g,SVG+"path",{"id":"patchtile_edge","d":outline_d,"style":"fill:none"})
A=el["tileA"]; at=list(r).index(A); r.remove(A)
N=copy.deepcopy(R); fix=lambda i: re.sub(r"_r(pat)?$", r"\1", i)
for e in N.iter():
    i=e.get("id")
    if i and i!="tileR":
        if fix(i)!=i: e.set("id",fix(i))
        else: assert e.tag.endswith("}rect"), i; del e.attrib["id"]
    st=e.get("style")
    if st and "url(#" in st: e.set("style", re.sub(r"url\(#([^)]+)\)", lambda m:"url(#%s)"%fix(m.group(1)), st))
N.set("id","tileA"); N.set(INK+"label","Hexagon tile"); del N.attrib["transform"]; N.set(SODI+"insensitive","true")
r.insert(at,N)
ids=[e.get("id") for e in r.iter() if e.get("id")]; assert len(ids)==len(set(ids)), [i for i in ids if ids.count(i)>1][:5]
allid=set(ids)
for e in r.iter():
    for m in re.findall(r"url\(#([^)]+)\)", e.get("style") or ""): assert m in allid, m
print(dict(cnt), "coverage %.1f%%"%(100*sum(F.A.area(p) for p in pieces)/F.A.area(F.A.Q)))
F.t.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
