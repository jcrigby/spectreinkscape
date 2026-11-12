import xml.etree.ElementTree as ET, sys
def info(f):
    r=ET.parse(f).getroot(); out={}
    for top in r:
        if top.get("id") in ("tileR","play"):
            for e in top.iter():
                if e.get("id") and e.tag.endswith(("}path","}g","}use")): out[e.get("id")]=(top.get("id"),e.tag.split('}')[1],e.get("d"),e.get("transform"))
            for e in top.iter():
                if not e.get("id"): print("element without id", e.tag, e.attrib)
    return out
a=info(sys.argv[1]); b=info("spectre.svg")
for k,v in b.items():
    if a.get(k)!=v: print("CHG" if k in a else "NEW",k,v, "\n    was", a.get(k))
for k in a:
    if k not in b: print("GONE",k,a[k])
