import math, re, sys, xml.etree.ElementTree as ET
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),(3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
dist = math.dist
def hexagon(k):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); t0 = math.atan2(a[1]-c[1], a[0]-c[0])
    return [(c[0]+50*math.cos(t0+j*math.pi/3), c[1]+50*math.sin(t0+j*math.pi/3)) for j in range(6)]
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
SVG = "{%s}" % NS["svg"]
tree = ET.parse("spectre.svg"); root = tree.getroot()
el = {e.get("id"): e for e in root.iter() if e.get("id")}
nums = lambda d: [tuple(map(float, p)) for p in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", d)]
blocked = [hexagon(k) for k in (5, 9, 11)]
for k in (1, 3, 7, 13): blocked += [nums(el["htile%02d" % k].get("d")), nums(el["htri%02d" % k].get("d"))]
ntri = 0
for e in el["centre"]:
    i = e.get("id") or ""
    if re.fullmatch(r"chex\d\d|ctri\d\d", i): blocked.append(nums(e.get("d")))
    if re.fullmatch(r"ctri\d\d", i): ntri = max(ntri, int(i[4:]))
pieces_area = sum(area(p) for p in blocked)
notches = [nums(el["hex%02din" % (k-1)].get("d")) for k in range(2, 15, 2)]
tile_area = area(Q)
anchors = [p for k in range(1, 15) for p in hexagon(k)] + [p for poly in blocked for p in poly]
def uniq(pts):
    out = []
    for p in pts:
        if not any(dist(p, q) < 0.05 for q in out): out.append(p)
    return out
anchors = uniq(anchors)
TA = 625*math.sqrt(3)
def fits(tri):
    if clip(Q, tri) < TA - 0.5: return False                      # must lie inside the straight outline
    return all(clip(tri, b) < 0.5 for b in blocked + notches)
def touching(tri):
    """How many of the triangle's sides lie along an existing piece edge."""
    n = 0
    for j in range(3):
        a, b = tri[j], tri[(j+1) % 3]; m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
        for poly in blocked + notches + [Q]:
            for k in range(len(poly)):
                p, q = poly[k], poly[(k+1) % len(poly)]; L = dist(p, q)
                if L < 1: continue
                d = abs((q[0]-p[0])*(m[1]-p[1]) - (q[1]-p[1])*(m[0]-p[0])) / L
                t = ((m[0]-p[0])*(q[0]-p[0]) + (m[1]-p[1])*(q[1]-p[1])) / (L*L)
                if d < 0.05 and 0 < t < 1: n += 1; break
            else: continue
            break
    return n
added = []
while True:
    cands = []
    for i in range(len(anchors)):
        for j in range(i+1, len(anchors)):
            a, b = anchors[i], anchors[j]
            if abs(dist(a, b) - 50) > 0.05: continue
            for sgn in (1, -1):
                c = ((a[0]+b[0])/2 - sgn*(b[1]-a[1])*r3, (a[1]+b[1])/2 + sgn*(b[0]-a[0])*r3)
                tri = [a, b, c]
                if fits(tri): cands.append((touching(tri), sum(1 for v in tri if any(dist(v, q) < 0.05 for q in anchors)), tri))
    if not cands: break
    cands.sort(key=lambda t: (-t[0], -t[1], t[2][0][1], t[2][0][0]))
    best = cands[0][2]; added.append(best); blocked.append(best); anchors = uniq(anchors + best)
filled = pieces_area + len(added)*TA
print("triangles that fit: %d; tile filled %.1f%% -> %.1f%%; still open %.0f px^2" % (len(added), 100*pieces_area/tile_area, 100*filled/tile_area, tile_area - filled))
if len(sys.argv) > 1 and sys.argv[1] == "write" and added:
    layer = el["centre"]; defs = el["centre_defs"]; W = 100/9
    for tri in added:
        ntri += 1; name = "ctri%02d" % ntri; c = (sum(p[0] for p in tri)/3, sum(p[1] for p in tri)/3)
        th = min(round(math.degrees(math.atan2(tri[(j+1) % 3][1]-tri[j][1], tri[(j+1) % 3][0]-tri[j][0]))) % 180 for j in range(3))
        pat = ET.SubElement(defs, SVG + "pattern", {"id": name + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
              "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*c, th, -W/2)})
        ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:#2060d0;stroke:none"})
        d = "M " + " L ".join("%.4f %.4f" % p for p in tri) + " Z"
        ET.SubElement(layer, SVG + "path", {"id": name + "bg", "d": d, "style": "fill:#ffffff;stroke:#2060d0;stroke-width:1.5;stroke-linejoin:round"})
        ET.SubElement(layer, SVG + "path", {"id": name, "d": d, "style": "fill:url(#%spat);stroke:none" % name})
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("wrote", len(added), "triangles; triangles on the tile now:", ntri)
