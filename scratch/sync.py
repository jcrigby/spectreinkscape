"""Regenerate the tiling patch's pieces from the left tile and refresh the locked right-hand copy."""
import copy, math, re, xml.etree.ElementTree as ET
NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd", "xlink": "http://www.w3.org/1999/xlink"}
for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
SVG, INK, SODI = "{%s}" % NS["svg"], "{%s}" % NS["inkscape"], "{%s}" % NS["sodipodi"]
tree = ET.parse("spectre.svg"); root = tree.getroot()
el = {e.get("id"): e for e in root.iter() if e.get("id")}
nums = lambda d: [tuple(map(float, p)) for p in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", d)]
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),(3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
def hexagon(k):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); t0 = math.atan2(a[1]-c[1], a[0]-c[0])
    return [(c[0]+50*math.cos(t0+j*math.pi/3), c[1]+50*math.sin(t0+j*math.pi/3)) for j in range(6)]
area = lambda p: abs(sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p)))) / 2
# ---- pieces on the left tile ----
pieces = [("hex", hexagon(k)) for k in (5, 9, 11) if "htile%02din" % k in el]
for k in (1, 3, 7, 13):
    half, tri = nums(el["htile%02d" % k].get("d")), nums(el["htri%02d" % k].get("d"))
    T = [p for p in tri if min(math.dist(p, q) for q in half) > 1][0]; pieces.append(("five6", half + [T]))
KIND = {"chex": "hex", "ctri": "tri", "cscal": "scal", "ctrap": "trap", "chalf": "scal", "ccomb": "comb", "cfive": "five6", "cpara": "para", "cstrip": "para", "cdiam": "diam", "ccorn": "corn", "ccust": "cust", "cbig": "half", "celong": "hex"}
for e in el["centre"]:
    m = re.fullmatch(r"(chex|ctri|cscal|ctrap|chalf|ccomb|cfive|cpara|cstrip|cdiam|ccorn|ccust|cbig|celong)\d\d", e.get("id") or "")
    if m: pieces.append((KIND[m.group(1)], nums(e.get("d"))))
# ---- tiling patch ----
g = el["patchtile"]; outline_d = el["patchtile_outline"].get("d")
for c in list(g): g.remove(c)
ET.SubElement(g, SVG + "path", {"id": "patchtile_outline", "d": outline_d})
FILL = {"hex": "#3db45c", "five6": "#e8463c", "tri": "#4a7fe0", "scal": "#f5a03a", "trap": "#9b59d0", "half": "#2aa7a0", "comb": "#9b59d0", "para": "#f5a03a", "diam": "#e0559f", "corn": "#d9b01c", "cust": "#e0559f"}
unit = lambda p: ((p[0]-200)/100, (350-p[1])/100)
for n, (kind, poly) in enumerate(pieces):
    ET.SubElement(g, SVG + "path", {"id": "patchpiece%02d" % n, "d": "M " + " L ".join("%.5f %.5f" % unit(p) for p in poly) + " Z",
        "style": "fill:%s;stroke:#ffffff;stroke-width:0.02;stroke-linejoin:round" % FILL[kind]})
ET.SubElement(g, SVG + "path", {"id": "patchtile_edge", "d": outline_d, "style": "fill:none"})
# ---- right-hand copy ----
at = list(root).index(el["tileR"]); old = sum(1 for _ in el["tileR"].iter()); root.remove(el["tileR"])
R = copy.deepcopy(el["tileA"]); ids = {e.get("id") for e in R.iter() if e.get("id")}
for e in R.iter():
    if e.get("id"): e.set("id", e.get("id") + "_r")
    st = e.get("style")
    if st and "url(#" in st: e.set("style", re.sub(r"url\(#([^)]+)\)", lambda m: "url(#%s_r)" % m.group(1) if m.group(1) in ids else m.group(0), st))
R.set("id", "tileR"); R.set(INK + "label", "Hexagon tile (locked copy)"); R.set("transform", "translate(560,0)"); R.set(SODI + "insensitive", "true")
root.insert(at, R)
allids = [e.get("id") for e in root.iter() if e.get("id")]; assert len(allids) == len(set(allids))
tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
from collections import Counter
print(dict(Counter(k for k, _ in pieces)), "| coverage %.1f%% | right copy %d -> %d elements | movable pieces kept: %d" % (100*sum(area(p) for _, p in pieces)/area(Q), old, sum(1 for _ in R.iter()), len(list(el["play"]))))
