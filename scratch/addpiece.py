"""Add one convex piece to the left tile's centre layer after checking it against everything else.
usage: addpiece.py ID COLOUR x1,y1 x2,y2 ...   (stripes run perpendicular to the first side)"""
import math, re, sys, xml.etree.ElementTree as ET
NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd", "xlink": "http://www.w3.org/1999/xlink"}
for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
SVG = "{%s}" % NS["svg"]
nums = lambda d: [tuple(map(float, p)) for p in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", d)]
area = lambda p: abs(sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p)))) / 2
def ccw(p): return p if sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p))) > 0 else p[::-1]
def clip(subject, convex):
    out = list(subject); convex = ccw(convex)
    for k in range(len(convex)):
        a, b = convex[k], convex[(k+1) % len(convex)]; nx, ny = -(b[1]-a[1]), b[0]-a[0]; inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j+1) % len(inp)]; fp, fq = (p[0]-a[0])*nx + (p[1]-a[1])*ny, (q[0]-a[0])*nx + (q[1]-a[1])*ny
            if fp >= 0: out.append(p)
            if (fp > 0 > fq) or (fq > 0 > fp): t = fp / (fp - fq); out.append((p[0]+t*(q[0]-p[0]), p[1]+t*(q[1]-p[1])))
        if len(out) < 3: return 0.0
    return area(out)
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),(3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
PIECE = r"(chex|ctri|cscal|ccomb|chalf|cpara|cfive|cstrip|cdiam|ccorn|ccust|cbig|celong|cpc)\d\d"
def load():
    tree = ET.parse("spectre.svg"); el = {e.get("id"): e for e in tree.getroot().iter() if e.get("id")}
    solid = {e.get("id"): nums(e.get("d")) for e in el["centre"] if re.fullmatch(PIECE, e.get("id") or "")}
    for k in (5, 9, 11):
        if "htile%02din" % k not in el: continue
        a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); t0 = math.atan2(a[1]-c[1], a[0]-c[0]); solid["whole hexagon %d" % k] = [(c[0]+50*math.cos(t0+j*math.pi/3), c[1]+50*math.sin(t0+j*math.pi/3)) for j in range(6)]
    for k in (1, 3, 7, 13): solid["5/6 hex %d" % k] = nums(el["htile%02d" % k].get("d")); solid["5/6 hex %d tri" % k] = nums(el["htri%02d" % k].get("d"))
    notch = {"notch %d" % k: nums(el["hex%02din" % (k-1)].get("d")) for k in range(2, 15, 2)}
    return tree, el, solid, notch
def corner(k, hour):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); th = math.radians(hour*30); return (c[0]+50*math.sin(th), c[1]-50*math.cos(th))
def piece_corner(poly, hour):
    c = (sum(p[0] for p in poly)/len(poly), sum(p[1] for p in poly)/len(poly))
    return c
def add(tree, el, solid, notch, nm, col, poly):
    hits = {k: round(clip(poly, v), 1) for k, v in {**solid, **notch}.items() if clip(poly, v) > 0.5}
    inside = clip(Q, poly)
    assert not hits and inside > area(poly) - 0.5, (hits, inside, area(poly))
    layer, defs = el["centre"], el["centre_defs"]; W = 100/9; c = (sum(p[0] for p in poly)/len(poly), sum(p[1] for p in poly)/len(poly))
    th = math.degrees(math.atan2(poly[1][1]-poly[0][1], poly[1][0]-poly[0][0])) % 180
    pat = ET.SubElement(defs, SVG + "pattern", {"id": nm + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
          "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*c, th, -W/2)})
    ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:%s;stroke:none" % col})
    d = "M " + " L ".join("%.4f %.4f" % p for p in poly) + " Z"
    ET.SubElement(layer, SVG + "path", {"id": nm + "bg", "d": d, "style": "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % col})
    ET.SubElement(layer, SVG + "path", {"id": nm, "d": d, "style": "fill:url(#%spat);stroke:none" % nm})
    solid[nm] = poly
    return 100*sum(area(v) for v in solid.values())/area(Q)
def describe(poly):
    n = len(poly); sides = [math.dist(poly[i], poly[(i+1) % n]) for i in range(n)]; ang = []
    for i in range(n):
        a, b, c = poly[i], poly[(i+1) % n], poly[i-1]
        ang.append(round(math.degrees(math.acos(((b[0]-a[0])*(c[0]-a[0]) + (b[1]-a[1])*(c[1]-a[1])) / (math.dist(a, b)*math.dist(a, c))))))
    par = [(i, j) for i in range(n) for j in range(i+1, n) if abs((poly[(i+1) % n][0]-poly[i][0])*(poly[(j+1) % n][1]-poly[j][1]) - (poly[(i+1) % n][1]-poly[i][1])*(poly[(j+1) % n][0]-poly[j][0])) < 1e-6]
    return "sides %s, angles %s, area %.0f, parallel side pairs %d" % (["%.1f" % s for s in sides], ang, area(poly), len(par))
