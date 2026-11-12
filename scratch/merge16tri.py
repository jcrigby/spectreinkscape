import math, re, sys, importlib.util, xml.etree.ElementTree as ET
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("ap", here + "/addpiece.py"); ap = importlib.util.module_from_spec(spec); spec.loader.exec_module(ap)
tree, el, solid, notch = ap.load()
SVG = "{http://www.w3.org/2000/svg}"
P16, T = solid["ccust01"], solid["ccorn02"]
def hull(pts):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    def half(ps):
        h = []
        for p in ps:
            while len(h) >= 2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 0.5: h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(pts[::-1]); return lo[:-1] + up[:-1]
def inside_union(p):
    def inpoly(q, V):
        s = None
        for i in range(len(V)):
            a, b = V[i], V[(i+1) % len(V)]; cr = (b[0]-a[0])*(q[1]-a[1]) - (b[1]-a[1])*(q[0]-a[0])
            if abs(cr) < 1e-3: continue
            if s is None: s = cr > 0
            elif (cr > 0) != s: return False
        return True
    return inpoly(p, P16) or inpoly(p, T)
# largest convex piece: keep the part of the triangle on 16's side of each of 16's edges that the triangle would otherwise wrap round
best = None
n = len(P16)
for i in range(n):                                   # try cutting the triangle with the line of each edge of 16
    a, b = P16[i], P16[(i+1) % n]; nx, ny = -(b[1]-a[1]), b[0]-a[0]
    c16 = (sum(p[0] for p in P16)/n, sum(p[1] for p in P16)/n)
    if (c16[0]-a[0])*nx + (c16[1]-a[1])*ny < 0: nx, ny = -nx, -ny
    part = []
    for j in range(3):
        p, q = T[j], T[(j+1) % 3]; fp, fq = (p[0]-a[0])*nx + (p[1]-a[1])*ny, (q[0]-a[0])*nx + (q[1]-a[1])*ny
        if fp >= -1e-6: part.append(p)
        if (fp > 1e-6 and fq < -1e-6) or (fq > 1e-6 and fp < -1e-6): t = fp/(fp-fq); part.append((p[0]+t*(q[0]-p[0]), p[1]+t*(q[1]-p[1])))
    if len(part) < 3: continue
    H = hull(P16 + part); A = ap.area(P16) + ap.area(part)
    if abs(ap.area(H) - A) < 1.0 and (best is None or A > best[0]): best = (A, H, part, i)
A, H, part, i = best
print("triangle %.0f px^2; part that can join 16 and stay convex: %.0f px^2 (cut along the line of 16's side from (%.1f, %.1f) to (%.1f, %.1f)); gap left: %.0f px^2"
      % (ap.area(T), ap.area(part), *P16[i], *P16[(i+1) % n], ap.area(T) - ap.area(part)))
print("new 16:", ap.describe(H))
if len(sys.argv) > 1 and sys.argv[1] == "write":
    layer, defs = el["centre"], el["centre_defs"]
    for k in ("ccust01", "ccorn02"):
        layer.remove(el[k]); layer.remove(el[k + "bg"]); defs.remove(el[k + "pat"]); solid.pop(k)
    if sum(H[j][0]*H[(j+1) % len(H)][1] - H[(j+1) % len(H)][0]*H[j][1] for j in range(len(H))) < 0: H = H[::-1]
    cov = ap.add(tree, el, solid, notch, "ccust01", "#d63a8c", H)
    el2 = {e.get("id"): e for e in tree.getroot().iter() if e.get("id")}
    el2["ccust01pat"].set("patternTransform", re.sub(r"rotate\([^)]*\)", "rotate(30)", el2["ccust01pat"].get("patternTransform")))
    c = (sum(p[0] for p in H)/len(H), sum(p[1] for p in H)/len(H))
    el2["num16"].set("x", "%.2f" % c[0]); el2["num16"].set("y", "%.2f" % (c[1] + 7))
    cl = el2["layer-corners"]; style = [e for e in cl][0].get("style")
    for e in list(cl):
        if (e.get("id") or "").startswith("corner16_"): cl.remove(e)
    hrs = [((90 - math.degrees(math.atan2(-(p[1]-c[1]), p[0]-c[0]))) / 30) % 12 for p in H]
    order = sorted(range(len(H)), key=lambda j: hrs[j]); used = set(); labs = {}
    for j in order:                                   # nearest free clock hour, never going backwards
        cand = sorted(range(1, 13), key=lambda h: min(abs(h - hrs[j]), 12 - abs(h - hrs[j])))
        lab = [h for h in cand if h not in used][0]; used.add(lab); labs[j] = lab
    for j in order:
        p = H[j]; t = ET.SubElement(cl, SVG + "text", {"id": "corner16_%02d" % labs[j], "x": "%.2f" % (c[0] + 0.8*(p[0]-c[0])), "y": "%.2f" % (c[1] + 0.8*(p[1]-c[1]) + 3.2), "style": style}); t.text = str(labs[j])
        print("   16,%-2d at (%.1f, %.1f)  [true clock position %.1f]" % (labs[j], *p, hrs[j]))
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8"); print("coverage %.1f%%" % cov)
