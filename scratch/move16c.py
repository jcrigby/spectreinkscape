import math, re, sys, importlib.util, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load(); SVG = "{http://www.w3.org/2000/svg}"
P = solid["ccust01"]; h15 = solid["chex01"]; c15 = (sum(p[0] for p in h15)/6, sum(p[1] for p in h15)/6)
t155 = (c15[0]+50*math.sin(math.radians(150)), c15[1]-50*math.cos(math.radians(150)))
cl = el["layer-corners"]
lab = {}
c = (sum(p[0] for p in P)/len(P), sum(p[1] for p in P)/len(P))
for e in cl:
    m = re.fullmatch(r"corner16_(\d\d)", e.get("id") or "")
    if m:
        x, y = float(e.get("x")), float(e.get("y")) - 3.2; q = (c[0] + (x-c[0])/0.8, c[1] + (y-c[1])/0.8)
        j = min(range(len(P)), key=lambda j: math.dist(P[j], q)); lab[int(m.group(1))] = j
i9, i10 = lab[9], lab[10]
print("16,9 (%.1f, %.1f) and 16,10 (%.1f, %.1f) -> 15,5 (%.1f, %.1f)" % (*P[i9], *P[i10], *t155))
new = [t155 if j == i9 else p for j, p in enumerate(P) if j != i10]
before = ap.area(P)
def convex(V):
    s = None
    for i in range(len(V)):
        a, b, c_ = V[i-1], V[i], V[(i+1) % len(V)]; cr = (b[0]-a[0])*(c_[1]-b[1]) - (b[1]-a[1])*(c_[0]-b[0])
        if abs(cr) < 1.0: continue
        if s is None: s = cr > 0
        elif (cr > 0) != s: return False
    return True
print("new 16:", ap.describe(new), "| convex:", convex(new), "| area %.0f -> %.0f" % (before, ap.area(new)))
layer, defs = el["centre"], el["centre_defs"]
for k in ("ccust01",): layer.remove(el[k]); layer.remove(el[k + "bg"]); defs.remove(el[k + "pat"]); solid.pop(k)
cov = ap.add(tree, el, solid, notch, "ccust01", "#d63a8c", new)
el2 = {e.get("id"): e for e in tree.getroot().iter() if e.get("id")}
el2["ccust01pat"].set("patternTransform", re.sub(r"rotate\([^)]*\)", "rotate(30)", el2["ccust01pat"].get("patternTransform")))
c = (sum(p[0] for p in new)/len(new), sum(p[1] for p in new)/len(new))
el2["num16"].set("x", "%.2f" % c[0]); el2["num16"].set("y", "%.2f" % (c[1] + 7))
style = [e for e in cl][0].get("style")
keepnames = {tuple(round(v, 1) for v in P[j]): h for h, j in lab.items() if h not in (9, 10)}
for e in list(cl):
    if (e.get("id") or "").startswith("corner16_"): cl.remove(e)
for p in new:
    h = keepnames.get(tuple(round(v, 1) for v in p), 9)
    t = ET.SubElement(cl, SVG + "text", {"id": "corner16_%02d" % h, "x": "%.2f" % (c[0] + 0.8*(p[0]-c[0])), "y": "%.2f" % (c[1] + 0.8*(p[1]-c[1]) + 3.2), "style": style}); t.text = str(h)
    print("   16,%-2d at (%.1f, %.1f)" % (h, *p))
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("no overlaps; coverage %.2f%%; still open %.0f px^2" % (cov, ap.area(ap.Q)*(1-cov/100)))
