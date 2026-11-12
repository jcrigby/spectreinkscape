import math, re, sys, importlib.util, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("al", here + "/alignplay.py"); al = importlib.util.module_from_spec(spec); spec.loader.exec_module(al)
Q, dist = al.Q, math.dist
def area(p): return abs(sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p)))) / 2
def ccw(p): return p if sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p))) > 0 else p[::-1]
def clip(subject, convex):
    out = list(subject); convex = ccw(convex)
    for k in range(len(convex)):
        a, b = convex[k], convex[(k+1) % len(convex)]; nx, ny = -(b[1]-a[1]), b[0]-a[0]
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j+1) % len(inp)]
            fp, fq = (p[0]-a[0])*nx + (p[1]-a[1])*ny, (q[0]-a[0])*nx + (q[1]-a[1])*ny
            if fp >= 0: out.append(p)
            if (fp > 0 > fq) or (fq > 0 > fp):
                t = fp / (fp - fq); out.append((p[0]+t*(q[0]-p[0]), p[1]+t*(q[1]-p[1])))
        if len(out) < 3: return 0.0
    return area(out)
NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd", "xlink": "http://www.w3.org/1999/xlink"}
for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
SVG, INK = "{%s}" % NS["svg"], "{%s}" % NS["inkscape"]
tree = ET.parse("spectre.svg"); root = tree.getroot()
el = {e.get("id"): e for e in root.iter() if e.get("id")}
nums = lambda d: [tuple(map(float, p)) for p in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", d)]
# what is already there on the left tile (convex parts), and what is off limits
solid = {}
for k in (5, 9, 11): solid["whole hexagon %d" % k] = [al.hexagon(k)]
for k in (1, 3, 7, 13): solid["5/6 hex %d" % k] = [nums(el["htile%02d" % k].get("d")), nums(el["htri%02d" % k].get("d"))]
notch = {"notch of hexagon %d" % k: [nums(el["hex%02din" % (k-1)].get("d"))] for k in range(2, 15, 2)}
problems = []
for i, pc in enumerate(al.pieces):
    name = "%s %s" % ("hexagon" if pc["n"] == 6 else "triangle", pc["id"])
    for label, parts in {**solid, **notch}.items():
        v = sum(clip(pc["placed"], part) for part in parts)
        if v > 0.5: problems.append("%s overlaps %s by %.0f px^2" % (name, label, v))
    for qc in al.pieces[i+1:]:
        v = clip(pc["placed"], qc["placed"])
        if v > 0.5: problems.append("%s overlaps %s %s by %.0f px^2" % (name, "hexagon" if qc["n"] == 6 else "triangle", qc["id"], v))
    inside = clip(pc["placed"], Q) if False else None
print("overlap check:", problems or "none")
if len(sys.argv) > 1 and sys.argv[1] == "write":
    A = el["tileA"]; kids = list(A)
    if "centre" in el: A.remove(el["centre"]); kids = list(A)
    first_red = min(kids.index(el["hex%02d%s" % (i, "out" if i % 2 == 0 else "in")]) for i in range(14))
    layer = ET.Element(SVG + "g", {INK + "groupmode": "layer", INK + "label": "Centre pieces", "id": "centre"}); A.insert(first_red, layer)
    defs = ET.SubElement(layer, SVG + "defs", {"id": "centre_defs"}); W = 100/9; nh = nt = 0
    for pc in sorted(al.pieces, key=lambda p: (-p["n"], p["c"][1], p["c"][0])):
        pts = pc["placed"]; c = (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
        if pc["n"] == 6: nh += 1; name, col = "chex%02d" % nh, "#1a9a3a"; th = round(math.degrees(pc["ang"])) % 60
        else: nt += 1; name, col = "ctri%02d" % nt, "#2060d0"; th = min((round(math.degrees(math.atan2(pts[(j+1) % 3][1]-pts[j][1], pts[(j+1) % 3][0]-pts[j][0]))) % 180 for j in range(3)))
        pat = ET.SubElement(defs, SVG + "pattern", {"id": name + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
              "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*c, th, -W/2)})
        ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:%s;stroke:none" % col})
        d = "M " + " L ".join("%.4f %.4f" % p for p in pts) + " Z"
        ET.SubElement(layer, SVG + "path", {"id": name + "bg", "d": d, "style": "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % col})
        ET.SubElement(layer, SVG + "path", {"id": name, "d": d, "style": "fill:url(#%spat);stroke:none" % name})
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
    print("drew %d hexagons and %d triangles on the left tile" % (nh, nt))
