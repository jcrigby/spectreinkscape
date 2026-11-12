import math, sys, importlib.util, numpy as np, xml.etree.ElementTree as ET
write = len(sys.argv) > 1 and sys.argv[1] == "write"; sys.argv = sys.argv[:1]
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("fl", here + "/fliplong.py"); fl = importlib.util.module_from_spec(spec)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(fl)
lc = fl.lc; C, R, Q, dist, arc, frame = lc.C, lc.R, lc.Q, lc.dist, lc.arc, lc.frame
def meets(a, b):
    d = dist(a, b); mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
    h = math.sqrt(max(R*R - d*d/4, 0)); px, py = -(b[1]-a[1])/d, (b[0]-a[0])/d
    return (mx+h*px, my+h*py), (mx-h*px, my-h*py)
def inpoly_pt(p):
    c = False
    for i in range(14):
        (x1, y1), (x2, y2) = Q[i], Q[(i+1) % 14]
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1]-y1)*(x2-x1)/(y2-y1): c = not c
    return c
def candidate(a, b):
    ca, cb = C[a], C[b]; d = dist(ca, cb); mid = ((ca[0]+cb[0])/2, (ca[1]+cb[1])/2)
    px, py = -(cb[1]-ca[1])/d, (cb[0]-ca[0])/d; h = math.sqrt(max(R*R - d*d/4, 0))
    for sgn in (1, -1):
        apex, axis = (mid[0]+sgn*h*px, mid[1]+sgn*h*py), (sgn*px, sgn*py)
        probe = (apex[0]+3*axis[0], apex[1]+3*axis[1])
        if inpoly_pt(probe) and all(dist(probe, C[j]) > R for j in C): break
    O = (apex[0]+R*axis[0], apex[1]+R*axis[1])
    Xa = max(meets(O, ca), key=lambda p: dist(p, apex)); Xb = max(meets(O, cb), key=lambda p: dist(p, apex))
    far = (O[0]+R*axis[0], O[1]+R*axis[1])
    seq = [(apex, Xa, ca), (Xa, far, O), (far, Xb, O), (Xb, apex, cb)]
    dpath = "M %.4f %.4f " % apex + " ".join(arc(p, q, c) for p, q, c in seq) + " Z"
    return dict(pair=(a, b), O=O, d=dpath, ca=ca, cb=cb, opening=round(180 - math.degrees(2*math.asin(min(d/2/R, 1)))))
SITES = [((1, 2), "A", "#8a3fc0"), ((9, 10), "A", "#8a3fc0")]
cands = []
for pr, kind, col in SITES:
    c = candidate(*pr); c.update(kind=kind, col=col, name="cand%02d%02d" % pr); cands.append(c)

xs, ys = np.meshgrid(np.arange(60, 640, 0.5), np.arange(40, 480, 0.5)); A = 0.25
D = lambda c, r=R: (xs-c[0])**2 + (ys-c[1])**2 < r*r
for c in cands: c["mask"] = D(c["O"]) & ~D(c["ca"]) & ~D(c["cb"])

# plain hpf with its spike pushed into the gap between circles 5 and 8, as far as it goes
c5, c8 = C[5], C[8]; g = dist(c5, c8); mid = ((c5[0]+c8[0])/2, (c5[1]+c8[1])/2)
perp = ((c8[0]-c5[0])/g, (c8[1]-c5[1])/g); axis = (-perp[1], perp[0])
if (C[6][0]-mid[0])*axis[0] + (C[6][1]-mid[1])*axis[1] < 0: axis = (-axis[0], -axis[1])     # point toward the pocket by 6 and 7
def hpf_at(adv):
    cusp = (mid[0]+adv*axis[0], mid[1]+adv*axis[1]); O = (cusp[0]-R*axis[0], cusp[1]-R*axis[1])
    va = (cusp[0]-R*perp[0], cusp[1]-R*perp[1]); vb = (cusp[0]+R*perp[0], cusp[1]+R*perp[1])
    return cusp, O, va, vb
gx, gy = np.meshgrid(np.arange(mid[0]-130, mid[0]+90, 0.2), np.arange(mid[1]-110, mid[1]+110, 0.2))
G = lambda c, r=R: (gx-c[0])**2 + (gy-c[1])**2 < r*r
solid = np.zeros(gx.shape, bool)
for j in C: solid |= G(C[j], R-0.05)
def hit(adv):
    cusp, O, va, vb = hpf_at(adv)
    return ((G(O) & ~G(va) & ~G(vb)) & solid).sum() * 0.04
def hit_by(adv):
    cusp, O, va, vb = hpf_at(adv); m = G(O) & ~G(va) & ~G(vb)
    return {j: round(float((m & G(C[j], R-0.05)).sum()*0.04), 1) for j in C if (m & G(C[j], R-0.05)).sum()*0.04 > 0.05}
lo, hi = -60.0, -20.0
assert not hit_by(lo) and hit_by(hi)
for _ in range(24):
    m_ = (lo+hi)/2
    if not hit_by(m_): lo = m_
    else: hi = m_
ADV = math.floor(lo*10)/10
def clear(adv):
    cusp, O, va, vb = hpf_at(adv)
    bl, br, back = (O[0]-R*perp[0], O[1]-R*perp[1]), (O[0]+R*perp[0], O[1]+R*perp[1]), (O[0]-R*axis[0], O[1]-R*axis[1])
    pts = [p_ for (p, q, c) in [(cusp, bl, va), (bl, back, O), (back, br, O), (br, cusp, vb)] for p_ in lc.sample(p, q, c, 600)]
    return min(dist(p_, C[j]) - R for p_ in pts for j in C)
while clear(ADV) < 0: ADV = round(ADV - 0.1, 1)
cusp, O, va, vb = hpf_at(ADV)
bl, br, back = (O[0]-R*perp[0], O[1]-R*perp[1]), (O[0]+R*perp[0], O[1]+R*perp[1]), (O[0]-R*axis[0], O[1]-R*axis[1])
hseq = [(cusp, bl, va), (bl, back, O), (back, br, O), (br, cusp, vb)]
hp = dict(pair=(), O=O, kind="hpf", col="#e00000", name="candhpf0508", opening=0,
          d="M %.4f %.4f " % cusp + " ".join(arc(p, q, c) for p, q, c in hseq) + " Z", mask=D(O) & ~D(va) & ~D(vb))
cands.append(hp)
tipgap = {j: round(min(dist(cusp, C[j]) - R, 999), 1) for j in (5, 6, 7, 8)}
print("hpf as deep as it goes: cusp %.1f px relative to the narrowest point of the 5-8 gap (negative = short of it); cusp at (%.1f, %.1f), dome centre (%.1f, %.1f); cusp clearance to circles %s" % (ADV, *cusp, *O, tipgap))
allpts = [p_ for (p, q, c) in hseq for p_ in lc.sample(p, q, c, 600)]
print("  closest approach of the hpf to each nearby circle (px):", {j: round(min(dist(p_, C[j]) - R for p_ in allpts), 2) for j in (4, 5, 8, 9, 2, 10)})
def longc(k):
    m, e, n = frame(k); F = (m[0]+R*e[0]+R*n[0], m[1]+R*e[1]+R*n[1])
    quarter = ((xs-m[0])*e[0]+(ys-m[1])*e[1] > 0) & ((xs-m[0])*n[0]+(ys-m[1])*n[1] > 0)
    return D(F) & ~D(C[k+1]) & ~D(C[k+2]) & ~(D(m) & ~quarter)
def rot(p, deg=9.73):
    a = math.radians(deg); cs, sn = math.cos(a), math.sin(a); x, y = p[0]-fl.c4[0], p[1]-fl.c4[1]
    return (fl.c4[0]+cs*x-sn*y, fl.c4[1]+sn*x+cs*y)
existing = {"long crescent at 5-6-7": ("longcres05bg_b", longc(5)), "long crescent at 11-12-13": ("longcres11bg_b", longc(11))}
clashes = []                                           # (candidate, kind, what, area)
for c in cands:
    for j in C:
        if j in c["pair"]: continue
        v = (c["mask"] & D(C[j], R-0.3)).sum()*A
        if v > 1: clashes.append((c, "circle", j, v))
    for nm, (eid, m) in existing.items():
        v = (c["mask"] & m).sum()*A
        if v > 1: clashes.append((c, "piece", (nm, eid), v))
for i in range(len(cands)):
    for j in range(i+1, len(cands)):
        v = (cands[i]["mask"] & cands[j]["mask"]).sum()*A
        if v > 1: clashes.append((cands[i], "cand", cands[j], v))
for c in cands:
    mine = [(k, w, v) for cc, k, w, v in clashes if cc is c] + [("cand", cc, v) for cc, k, w, v in clashes if k == "cand" and w is c]
    desc = ["circle %d: %.0f" % (w, v) if k == "circle" else "%s: %.0f" % (w[0], v) if k == "piece" else "candidate %s: %.0f" % (w["name"], v) for k, w, v in mine]
    print("%-5s at %s (%.0f px^2): %s" % (c["kind"], ",".join(map(str, c["pair"])) or "5-8 gap", c["mask"].sum()*A, "; ".join(desc) or "no overlap"))

if write:
    NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
    for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
    SVG, INK = "{%s}" % NS["svg"], "{%s}" % NS["inkscape"]
    tree = ET.parse("spectre.svg"); root = tree.getroot()
    el = {e.get("id"): e for e in root.iter() if e.get("id")}
    if "cand_b" in el:
        par = {c: p_ for p_ in root.iter() for c in p_}; par[el["cand_b"]].remove(el["cand_b"])
    B = el["tileB"]; kids = list(B); at = kids.index(el["arc00out_b"])
    layer = ET.Element(SVG + "g", {INK + "groupmode": "layer", INK + "label": "hpf candidates", "id": "cand_b"})
    B.insert(at, layer)
    defs = ET.SubElement(layer, SVG + "defs", {"id": "cand_defs_b"})
    for c in cands:
        ET.SubElement(layer, SVG + "path", {"id": c["name"] + "_b", "d": c["d"],
            "style": "fill:%s;fill-opacity:0.3;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % (c["col"], c["col"])})
    n = 0
    for c, kind, what, v in clashes:
        if kind == "cand" and (v > 3000 or v < 5): continue      # same-spot pair / hairline: leave to the see-through fills
        n += 1; cid = "candclip%02d_b" % n
        cp = ET.SubElement(defs, SVG + "clipPath", {"id": cid, "clipPathUnits": "userSpaceOnUse"})
        if kind == "circle": ET.SubElement(cp, SVG + "circle", {"cx": "%.4f" % C[what][0], "cy": "%.4f" % C[what][1], "r": "50"})
        elif kind == "piece": ET.SubElement(cp, SVG + "path", {"d": el[what[1]].get("d")})
        else: ET.SubElement(cp, SVG + "path", {"d": what["d"]})
        ET.SubElement(layer, SVG + "path", {"id": "candclash%02d_b" % n, "d": c["d"], "clip-path": "url(#%s)" % cid,
            "style": ("fill:#111111;fill-opacity:0.5;stroke:none" if kind == "cand" else "fill:#d0006f;fill-opacity:0.9;stroke:none")})
    for c in cands:
        t = ET.SubElement(layer, SVG + "text", {"id": c["name"] + "lbl_b", "x": "%.2f" % c["O"][0], "y": "%.2f" % (c["O"][1] + 5),
            "style": "font-family:sans-serif;font-weight:bold;font-size:14px;text-anchor:middle;fill:#222222;stroke:none"})
        t.text = c["kind"]
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
    print("wrote", len(cands), "candidates and", n, "overlap markers")
