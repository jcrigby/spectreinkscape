import math, re, sys, importlib.util, io, contextlib, itertools, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ft", here + "/filltri.py"); ft = importlib.util.module_from_spec(spec)
argv = sys.argv; sys.argv = argv[:1]
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(ft)
Q, dist, clip, area, uniq = ft.Q, ft.dist, ft.clip, ft.area, ft.uniq
def corner(k, hour):
    a, b = Q[k-1], Q[k % 14]; c = ((a[0]+b[0])/2, (a[1]+b[1])/2); th = math.radians(hour*30)
    p = (c[0]+50*math.sin(th), c[1]-50*math.cos(th))
    assert any(dist(p, q) < 1e-6 for q in ft.hexagon(k)), (k, hour)
    return p
T1 = [corner(8, 4), corner(6, 9), corner(6, 11)]
T2 = [corner(2, 3), corner(2, 1), corner(3, 12)]
def describe(T):
    s = sorted(dist(T[i], T[(i+1) % 3]) for i in range(3))
    ang = []
    for i in range(3):
        a, b, c = T[i], T[(i+1) % 3], T[(i+2) % 3]
        ang.append(math.degrees(math.acos(((b[0]-a[0])*(c[0]-a[0]) + (b[1]-a[1])*(c[1]-a[1])) / (dist(a, b)*dist(a, c)))))
    return s, sorted(ang)
def hand(T):                                           # sign of the turn when walking shortest -> middle -> longest side's opposite vertices
    order = sorted(range(3), key=lambda i: dist(T[(i+1) % 3], T[(i+2) % 3]))      # vertex opposite shortest, middle, longest side
    a, b, c = T[order[0]], T[order[1]], T[order[2]]
    return 1 if (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]) > 0 else -1
for nm, T in (("8,4 / 6,9 / 6,11", T1), ("2,3 / 2,1 / 3,12", T2)):
    s, an = describe(T)
    print("triangle %s: sides %s, angles %s, area %.1f, hand %+d" % (nm, ["%.2f" % x for x in s], ["%.1f" % x for x in an], area(T), hand(T)))
SIDES = sorted(dist(T1[i], T1[(i+1) % 3]) for i in range(3)); TA = area(T1)
blocked, notches = list(ft.blocked), ft.notches
def fits(tri, extra=()):
    if clip(Q, tri) < TA - 0.5: return False
    return all(clip(tri, b) < 0.5 for b in blocked + notches + list(extra))
for nm, T in (("first", T1), ("second", T2)):
    over = {i: round(clip(T, b), 1) for i, b in enumerate(blocked + notches) if clip(T, b) > 0.5}
    print("  %s triangle: inside outline %.1f of %.1f; overlaps: %s" % (nm, clip(Q, T), TA, over or "none"))
anchors = uniq(ft.anchors)
def third(a, b, la, lb, sgn):
    """Point at distance la from a and lb from b, on side sgn of a->b."""
    d = dist(a, b); x = (la*la - lb*lb + d*d) / (2*d); h2 = la*la - x*x
    if h2 < 0: return None
    h = math.sqrt(h2); ux, uy = (b[0]-a[0])/d, (b[1]-a[1])/d
    return (a[0]+x*ux - sgn*h*uy, a[1]+x*uy + sgn*h*ux)
cands = []
for i, j in itertools.combinations(range(len(anchors)), 2):
    a, b = anchors[i], anchors[j]; d = dist(a, b)
    for k, L in enumerate(SIDES):
        if abs(d - L) > 0.05: continue
        la, lb = [SIDES[m] for m in range(3) if m != k]
        for la_, lb_ in ((la, lb), (lb, la)):
            for sgn in (1, -1):
                c = third(a, b, la_, lb_, sgn)
                if c is None: continue
                tri = [a, b, c]
                if fits(tri): cands.append(tri)
key = lambda t: tuple(sorted((round(p[0], 1), round(p[1], 1)) for p in t))
seen = {}
for t in cands: seen.setdefault(key(t), t)
cands = list(seen.values())
print("distinct placements with at least two corners on existing corners that fit:", len(cands))
for t in cands:
    onanch = sum(1 for v in t if any(dist(v, q) < 0.05 for q in anchors))
    print("   (%.1f,%.1f) (%.1f,%.1f) (%.1f,%.1f)  hand %+d  corners on existing corners: %d%s" % (*t[0], *t[1], *t[2], hand(t), onanch,
          "  <- one you named" if key(t) in (key(T1), key(T2)) else ""))
# largest set with no two overlapping
best = []
def grow(chosen, rest):
    global best
    if len(chosen) > len(best): best = list(chosen)
    if len(chosen) + len(rest) <= len(best): return
    for n, t in enumerate(rest):
        if all(clip(t, c) < 0.5 for c in chosen): grow(chosen + [t], rest[n+1:])
must = [t for t in cands if key(t) in (key(T1), key(T2))]
others = [t for t in cands if key(t) not in (key(T1), key(T2)) and all(clip(t, m) < 0.5 for m in must)]
grow(list(must), others)
clean = [t for t in cands if all(any(dist(v, q) < 0.05 for q in anchors) for v in t)]
assert all(clip(a, b) < 0.5 for a, b in itertools.combinations(clean, 2))
print("placements with all three corners on existing corners:", len(clean))
best = clean
print("largest non-overlapping set including the two named:", len(best), "| hands:", [hand(t) for t in best])
if len(argv) > 1 and argv[1] == "write":
    NS = {"svg": "http://www.w3.org/2000/svg"}; SVG = "{%s}" % NS["svg"]
    tree, el = ft.tree, ft.el; layer, defs = el["centre"], el["centre_defs"]; W = 100/9
    for n, tri in enumerate(best, 1):
        name = "cscal%02d" % n; c = (sum(p[0] for p in tri)/3, sum(p[1] for p in tri)/3)
        j = max(range(3), key=lambda j: dist(tri[j], tri[(j+1) % 3])); th = math.degrees(math.atan2(tri[(j+1) % 3][1]-tri[j][1], tri[(j+1) % 3][0]-tri[j][0])) % 180
        pat = ET.SubElement(defs, SVG + "pattern", {"id": name + "pat", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
              "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*c, th, -W/2)})
        ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:#f08a00;stroke:none"})
        d = "M " + " L ".join("%.4f %.4f" % p for p in tri) + " Z"
        ET.SubElement(layer, SVG + "path", {"id": name + "bg", "d": d, "style": "fill:#ffffff;stroke:#f08a00;stroke-width:1.5;stroke-linejoin:round"})
        ET.SubElement(layer, SVG + "path", {"id": name, "d": d, "style": "fill:url(#%spat);stroke:none" % name})
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("wrote", len(best))
