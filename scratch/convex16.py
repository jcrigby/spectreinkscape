import math, sys, itertools, importlib.util
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
def hull(pts):
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    def half(ps):
        h = []
        for p in ps:
            while len(h) >= 2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 1e-7: h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(pts[::-1]); return lo[:-1] + up[:-1]
cen = lambda p: (sum(q[0] for q in p)/len(p), sum(q[1] for q in p)/len(p))
base = "cfive01"; c16 = cen(solid[base])
near = [k for k, v in solid.items() if k != base and math.dist(cen(v), c16) < 130]
print("16 is", ap.describe(solid[base])); print("pieces within reach:", near)
def shares_edge(a, b):
    for i in range(len(a)):
        p, q = a[i], a[(i+1) % len(a)]
        for j in range(len(b)):
            r, s = b[j], b[(j+1) % len(b)]
            cr = lambda u, v, w: (v[0]-u[0])*(w[1]-u[1]) - (v[1]-u[1])*(w[0]-u[0])
            if abs(cr(p, q, r)) < 0.05 and abs(cr(p, q, s)) < 0.05:
                d = (q[0]-p[0], q[1]-p[1]); L = math.dist(p, q)
                t = sorted(((r[0]-p[0])*d[0] + (r[1]-p[1])*d[1]) / L**2 for r in (r, s))
                if min(t[1], 1) - max(t[0], 0) > 0.02: return True
    return False
print("neighbours sharing an edge with 16:", [k for k in near if shares_edge(solid[base], solid[k])])
results = []
for r in range(0, len(near)+1):
    for combo in itertools.combinations(near, r):
        polys = [solid[base]] + [solid[k] for k in combo]
        A = sum(ap.area(p) for p in polys); H = hull([q for p in polys for q in p])
        if abs(ap.area(H) - A) < 1.0: results.append((A, combo, H))
results.sort(key=lambda t: -t[0])
print("convex unions containing 16: %d" % len(results))
for A, combo, H in results[:8]: print("   area %5.0f, %d corners: 16 + %s" % (A, len(H), list(combo) or "nothing"))
if len(sys.argv) > 1 and sys.argv[1] == "write":
    import xml.etree.ElementTree as ET, re
    A, combo, H = results[0]
    layer, defs = el["centre"], el["centre_defs"]
    for k in (base,) + combo:
        layer.remove(el[k]); layer.remove(el[k + "bg"]); defs.remove(el[k + "pat"]); solid.pop(k)
    # order the outline starting from 16,12 going clockwise on screen
    area2 = sum(H[i][0]*H[(i+1) % len(H)][1] - H[(i+1) % len(H)][0]*H[i][1] for i in range(len(H)))
    if area2 < 0: H = H[::-1]
    cov = ap.add(tree, el, solid, notch, "ccust01", "#d63a8c", H)
    el2 = {e.get("id"): e for e in tree.getroot().iter() if e.get("id")}
    el2["ccust01pat"].set("patternTransform", re.sub(r"rotate\([^)]*\)", "rotate(30)", el2["ccust01pat"].get("patternTransform")))
    c = cen(H); el2["num16"].set("x", "%.2f" % c[0]); el2["num16"].set("y", "%.2f" % (c[1] + 7))
    cl = el2["layer-corners"]; style = [e for e in cl][0].get("style")
    for e in list(cl):
        if (e.get("id") or "").startswith("corner16_"): cl.remove(e)
    SVG = "{http://www.w3.org/2000/svg}"; names = []
    for p in H:
        hour = round((90 - math.degrees(math.atan2(-(p[1]-c[1]), p[0]-c[0]))) / 30 * 2) / 2 % 12 or 12
        lab = ("%g" % hour)
        t = ET.SubElement(cl, SVG + "text", {"id": "corner16_%s" % lab.replace(".", "h"), "x": "%.2f" % (c[0] + 0.8*(p[0]-c[0])), "y": "%.2f" % (c[1] + 0.8*(p[1]-c[1]) + 3.2), "style": style}); t.text = lab
        names.append((lab, "%.1f" % p[0], "%.1f" % p[1]))
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
    print("merged: 16 +", list(combo)); print("new 16:", ap.describe(H)); print("corner labels:", names); print("coverage %.1f%%" % cov)
