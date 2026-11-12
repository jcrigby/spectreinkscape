import math, re, sys, importlib.util, io, contextlib, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("t3", here + "/trap3.py"); t3 = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(t3)
sf = t3.sf; el, tree, clip, area, dist = sf.el, sf.tree, sf.clip, sf.area, sf.dist
W = t3.mapped([sf.corner(1, 1), sf.corner(14, 2), sf.corner(14, 4)])
tri = sf.ft.nums(el["ctri08"].get("d"))
print("removing ctri08: corners", [(round(x, 1), round(y, 1)) for x, y in tri], "centre (%.1f, %.1f)" % (sum(p[0] for p in tri)/3, sum(p[1] for p in tri)/3))
others = {k: round(clip(W, v), 1) for k, v in t3.labels.items() if k != "ctri08" and clip(W, v) > 0.5}
assert not others and clip(sf.Q, W) > area(W) - 0.5, others
anchors = [p for k, v in t3.labels.items() if k != "ctri08" for p in v] + sf.ft.anchors
print("new trapezoid corners:", [(round(x, 1), round(y, 1), "on a corner" if any(dist((x, y), q) < 0.05 for q in anchors) else "free") for x, y in W])
layer, defs = el["centre"], el["centre_defs"]
for i in ("ctri08", "ctri08bg"): layer.remove(el[i])
defs.remove(el["ctri08pat"])
SVG = "{http://www.w3.org/2000/svg}"; Wd = 100/9; nm = "ctrap03"; c = (sum(p[0] for p in W)/4, sum(p[1] for p in W)/4)
j = max(range(4), key=lambda j: (round(dist(W[j], W[(j+1) % 4]), 1), -j)); th = math.degrees(math.atan2(W[(j+1) % 4][1]-W[j][1], W[(j+1) % 4][0]-W[j][0])) % 180
pat = ET.SubElement(defs, SVG + "pattern", {"id": nm + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*Wd), "height": "%.5f" % (2*Wd),
      "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*c, th, -Wd/2)})
ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % Wd, "height": "%.5f" % (2*Wd), "style": "fill:#8a3fc0;stroke:none"})
d = "M " + " L ".join("%.4f %.4f" % p for p in W) + " Z"
ET.SubElement(layer, SVG + "path", {"id": nm + "bg", "d": d, "style": "fill:#ffffff;stroke:#8a3fc0;stroke-width:1.5;stroke-linejoin:round"})
ET.SubElement(layer, SVG + "path", {"id": nm, "d": d, "style": "fill:url(#%spat);stroke:none" % nm})
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
filled = sum(area(v) for k, v in t3.labels.items() if not k.startswith("notch") and k != "ctri08") + area(W)
print("tile filled: %.1f%% (was %.1f%%)" % (100*filled/area(sf.Q), 100*(filled - area(W) + area(tri))/area(sf.Q)))
