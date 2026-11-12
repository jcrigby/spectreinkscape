import math, re, sys, itertools, importlib.util, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load(); SVG = "{http://www.w3.org/2000/svg}"
h11 = solid["whole hexagon 11"]; tris = {k: v for k, v in solid.items() if k.startswith("ctri")}
def hull(pts):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    def side(ps):
        h = []
        for p in ps:
            while len(h) >= 2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 0.5: h.pop()
            h.append(p)
        return h
    lo, up = side(pts), side(pts[::-1]); return lo[:-1] + up[:-1]
found = []
for r in range(len(tris), 0, -1):
    for combo in itertools.combinations(sorted(tris), r):
        polys = [h11] + [tris[k] for k in combo]; H = hull([p for q in polys for p in q])
        if abs(ap.area(H) - sum(ap.area(q) for q in polys)) < 1.0: found.append((r, combo, H))
print("convex unions of hexagon 11 with blue triangles:", [(r, c) for r, c, _ in found])
r, combo, H = found[0]; assert r == 4
left = [k for k in tris if k not in combo]
print("elongated 11 = hexagon 11 +", list(combo), "| blue triangle left over:", left, [("%.1f" % x, "%.1f" % y) for x, y in tris[left[0]]])
print("shape:", ap.describe(H))
layer, defs = el["centre"], el["centre_defs"]
A = [e for e in tree.getroot().iter() if e.get("id") == "tileA"][0]
for i in ("htile11", "htile11bg", "htile11in", "htile11inbg"): A.remove(el[i])
el["hex_defs"].remove(el["hstripe11"])
for k in combo:
    layer.remove(el[k]); layer.remove(el[k + "bg"]); defs.remove(el[k + "pat"]); solid.pop(k)
solid.pop("whole hexagon 11")
if sum(H[j][0]*H[(j+1) % len(H)][1] - H[(j+1) % len(H)][0]*H[j][1] for j in range(len(H))) < 0: H = H[::-1]
c11 = (sum(p[0] for p in h11)/6, sum(p[1] for p in h11)/6)
k0 = min(range(len(H)), key=lambda j: math.dist(H[j], (c11[0]-50, c11[1]))); H = H[k0:] + H[:k0]        # start at old corner 9
assert math.dist(H[0], (c11[0]-50, c11[1])) < 0.05
# clockwise on screen from corner 9
if (H[1][1] > H[0][1]): H = [H[0]] + H[1:][::-1]
hits = {k: round(ap.clip(H, v), 1) for k, v in {**solid, **notch}.items() if ap.clip(H, v) > 0.5}; assert not hits, hits
W = 100/9; nm = "celong11"
pat = ET.SubElement(defs, SVG + "pattern", {"id": nm + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
      "patternTransform": "translate(%.4f %.4f) rotate(0) translate(%.5f 0)" % (*c11, -W/2)})
ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:#1a9a3a;stroke:none"})
d = "M " + " L ".join("%.4f %.4f" % p for p in H) + " Z"
ET.SubElement(layer, SVG + "path", {"id": nm + "bg", "d": d, "style": "fill:#ffffff;stroke:#1a9a3a;stroke-width:1.5;stroke-linejoin:round"})
ET.SubElement(layer, SVG + "path", {"id": nm, "d": d, "style": "fill:url(#%spat);stroke:none" % nm})
cl = el["layer-corners"]; style = [e for e in cl][0].get("style"); c = (sum(p[0] for p in H)/6, sum(p[1] for p in H)/6)
for e in list(cl):
    if (e.get("id") or "").startswith("corner11_"): cl.remove(e)
for lab, p in zip((9, 11, 1, 3, 5, 7), H):
    t = ET.SubElement(cl, SVG + "text", {"id": "corner11_%02d" % lab, "x": "%.2f" % (c[0] + 0.82*(p[0]-c[0])), "y": "%.2f" % (c[1] + 0.82*(p[1]-c[1]) + 3.2), "style": style}); t.text = str(lab)
    print("   11,%-2d at (%.1f, %.1f)" % (lab, *p))
el["num11"].set("x", "%.2f" % c[0]); el["num11"].set("y", "%.2f" % (c[1] + 7))
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
solid[nm] = H; print("coverage %.1f%%" % (100*sum(ap.area(v) for v in solid.values())/ap.area(ap.Q)))
