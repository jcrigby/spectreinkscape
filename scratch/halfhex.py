import math, re, sys, importlib.util, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("sf", here + "/shapefit.py"); sf = importlib.util.module_from_spec(spec); spec.loader.exec_module(sf)
dist, corner, clip, area, el, tree, Q = sf.dist, sf.corner, sf.clip, sf.area, sf.el, sf.tree, sf.Q
A, B, C = corner(13, 2), corner(13, 4), corner(14, 2)
assert dist(B, corner(14, 12)) < 1e-6
# the hexagon these three consecutive corners belong to, and the two possible fourth corners
O = (A[0] + C[0] - B[0], A[1] + C[1] - B[1])               # centre: for a regular hexagon, centre = A + C - B
assert all(abs(dist(O, p) - 50) < 1e-6 for p in (A, B, C))
nxt = (2*O[0] - A[0], 2*O[1] - A[1]); prv = (2*O[0] - C[0], 2*O[1] - C[1])   # opposite A (follows C), opposite C (precedes A)
options = {"continuing past 14,2": [A, B, C, nxt], "continuing back before 13,2": [prv, A, B, C]}
labels = {}
for e in el["centre"]:
    i = e.get("id") or ""
    if re.fullmatch(r"(chex|ctri|cscal|ctrap)\d\d", i): labels[i] = sf.ft.nums(e.get("d"))
for k in (5, 9, 11): labels["whole hexagon %d" % k] = sf.ft.hexagon(k)
for k in (1, 3, 7, 13): labels["5/6 hex %d" % k] = sf.ft.nums(el["htile%02d" % k].get("d")); labels["5/6 hex %d triangle" % k] = sf.ft.nums(el["htri%02d" % k].get("d"))
for k in range(2, 15, 2): labels["notch %d" % k] = sf.ft.nums(el["hex%02din" % (k-1)].get("d"))
res = {}
for nm, poly in options.items():
    hits = {k: round(clip(poly, v)) for k, v in labels.items() if clip(poly, v) > 0.5}
    res[nm] = hits
    print("%s: 4th corner (%.1f, %.1f) [%s]; area %.0f; inside outline %.0f; overlaps %s" % (nm, *(poly[3] if poly[0] is A else poly[0]), sf.name(poly[3] if poly[0] is A else poly[0]), area(poly), clip(Q, poly), hits))
choice = [nm for nm, hits in res.items() if len(hits) == 2 and all(k.startswith("ctri") for k in hits)]
print("option that costs exactly two triangles:", choice)
if len(sys.argv) > 1 and sys.argv[1] == "write":
    assert len(choice) == 1
    poly = options[choice[0]]; layer, defs = el["centre"], el["centre_defs"]; SVG = "{http://www.w3.org/2000/svg}"
    for t in res[choice[0]]:
        layer.remove(el[t]); layer.remove(el[t + "bg"]); defs.remove(el[t + "pat"])
    W = 100/9; nm = "chalf01"; a, b = poly[0], poly[3]; m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    th = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0])) % 180
    pat = ET.SubElement(defs, SVG + "pattern", {"id": nm + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
          "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*m, th, -W/2)})
    ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:#0a9396;stroke:none"})
    d = "M " + " L ".join("%.4f %.4f" % p for p in poly) + " Z"
    ET.SubElement(layer, SVG + "path", {"id": nm + "bg", "d": d, "style": "fill:#ffffff;stroke:#0a9396;stroke-width:1.5;stroke-linejoin:round"})
    ET.SubElement(layer, SVG + "path", {"id": nm, "d": d, "style": "fill:url(#%spat);stroke:none" % nm})
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
    left = {k: v for k, v in labels.items() if not k.startswith("notch") and k not in res[choice[0]]}
    print("removed %s; coverage now %.1f%%" % (sorted(res[choice[0]]), 100*(sum(area(v) for v in left.values()) + area(poly))/area(Q)))
