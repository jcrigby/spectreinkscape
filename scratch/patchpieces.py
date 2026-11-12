import math, re, sys, importlib.util, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("al", here + "/alignplay.py"); al = importlib.util.module_from_spec(spec)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(al)
NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd", "xlink": "http://www.w3.org/1999/xlink"}
for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
SVG = "{%s}" % NS["svg"]
tree = ET.parse("spectre.svg"); root = tree.getroot()
el = {e.get("id"): e for e in root.iter() if e.get("id")}
nums = lambda d: [tuple(map(float, p)) for p in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", d)]
unit = lambda p: ((p[0]-200)/100, (350-p[1])/100)                     # left-tile px -> tile units, y up
pieces = []                                                          # (kind, polygon in px)
for k in (5, 9, 11): pieces.append(("hex", al.hexagon(k)))
for k in (1, 3, 7, 13):
    half, tri = nums(el["htile%02d" % k].get("d")), nums(el["htri%02d" % k].get("d"))
    assert len(half) == 4 and len(tri) == 3
    T = [p for p in tri if min(math.dist(p, q) for q in half) > 1][0]
    pieces.append(("five6", half + [T]))
for e in el["centre"]:
    i = e.get("id") or ""
    if re.fullmatch(r"chex\d\d", i): pieces.append(("hex", nums(e.get("d"))))
    if re.fullmatch(r"ctri\d\d", i): pieces.append(("tri", nums(e.get("d"))))
area = lambda p: abs(sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p)))) / 2
old = el["patchtile"]; outline_d = old.get("d") if old.tag.endswith("}path") else [c for c in old if c.get("id") == "patchtile_outline"][0].get("d")
outline = nums(outline_d)
defs = el["patch_defs"]; defs.remove(old)
g = ET.SubElement(defs, SVG + "g", {"id": "patchtile"})
ET.SubElement(g, SVG + "path", {"id": "patchtile_outline", "d": outline_d})
FILL = {"hex": "#3db45c", "five6": "#e8463c", "tri": "#4a7fe0"}
for n, (kind, poly) in enumerate(pieces):
    ET.SubElement(g, SVG + "path", {"id": "patchpiece%02d" % n, "d": "M " + " L ".join("%.5f %.5f" % unit(p) for p in poly) + " Z",
        "style": "fill:%s;stroke:#ffffff;stroke-width:0.02;stroke-linejoin:round" % FILL[kind]})
ET.SubElement(g, SVG + "path", {"id": "patchtile_edge", "d": outline_d, "style": "fill:none"})
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
filled = sum(area(p) for _, p in pieces) / 1e4; total = area(outline)
from collections import Counter
print(dict(Counter(k for k, _ in pieces)), "| filled %.3f of %.3f tile units^2 = %.1f%%" % (filled, total, 100*filled/total))
