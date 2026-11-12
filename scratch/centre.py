import math, sys, importlib.util, io, contextlib, numpy as np, xml.etree.ElementTree as ET
write = len(sys.argv) > 1 and sys.argv[1] == "write"; sys.argv = sys.argv[:1]
here = __file__.rsplit("/", 1)[0]
spec = importlib.util.spec_from_file_location("cd", here + "/candidates.py"); cd = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(cd)
C, R, Q, dist, arc, frame = cd.C, cd.R, cd.Q, cd.dist, cd.arc, cd.frame
xs, ys = np.meshgrid(np.arange(60, 640, 0.25), np.arange(40, 480, 0.25)); A_ = 0.0625
D = lambda c, r=R: (xs-c[0])**2 + (ys-c[1])**2 < r*r
def half_hpf(cusp, axis, N, name):
    """Half of an hpf: straight edge from cusp back along -axis for 100, concave flank on the circle centred N, quarter dome."""
    O = (cusp[0]-R*axis[0], cusp[1]-R*axis[1]); perp = ((N[0]-cusp[0])/R, (N[1]-cusp[1])/R)
    assert abs(dist(N, cusp) - R) < 1e-6 and abs(perp[0]*axis[0] + perp[1]*axis[1]) < 1e-9
    shoulder = (O[0]+R*perp[0], O[1]+R*perp[1]); back = (O[0]-R*axis[0], O[1]-R*axis[1])
    d = "M %.4f %.4f %s %s Z" % (*cusp, arc(cusp, shoulder, N), arc(shoulder, back, O))
    side = (xs-cusp[0])*perp[0] + (ys-cusp[1])*perp[1] > 0
    hand = "left" if (-axis[1])*perp[0] + axis[0]*perp[1] < 0 else "right"     # which side of the straight edge the flank is on, looking from cusp to back
    return dict(name=name, kind="half hpf", d=d, cusp=cusp, axis=axis, O=O, shoulder=shoulder, back=back, mask=D(O) & ~D(N) & side, col="#2060d0", hand=hand)
pieces = []
# 1. hugging circle 8, shoulder on the 8/9 corner, cusp through the 5-8 gap
c8, P8 = C[8], Q[8]
axis8 = ((c8[0]-P8[0])/R, (c8[1]-P8[1])/R)
u = (-axis8[1], axis8[0])
if dist((c8[0]+R*u[0], c8[1]+R*u[1]), C[5]) > dist((c8[0]-R*u[0], c8[1]-R*u[1]), C[5]): u = (-u[0], -u[1])
h8 = half_hpf((c8[0]+R*u[0], c8[1]+R*u[1]), axis8, c8, "halfhpf08"); pieces.append(h8)
# 2. variant A between 9 and 10 (unchanged from the candidate)
a = [c for c in cd.cands if c.get("pair") == (9, 10)][0]
ax_a = ((a["O"][0]-a["ca"][0]) , 0)
apexA = max(cd.meets(a["ca"], a["cb"]), key=lambda p: -dist(p, a["O"]))
axA = ((a["O"][0]-apexA[0])/R, (a["O"][1]-apexA[1])/R)
pieces.append(dict(name="varA0910", kind="A", d=a["d"], cusp=apexA, axis=(-axA[0], -axA[1]), O=a["O"], mask=D(a["O"]) & ~D(a["ca"]) & ~D(a["cb"]), col="#8a3fc0", hand="-"))
# 3. half hpf at the 10/11 joint: the half that hugs circle 11
P10 = Q[10]; c10, c11 = C[10], C[11]
down = (-(c11[1]-c10[1])/100, (c11[0]-c10[0])/100)
if not cd.inpoly_pt((P10[0]+5*down[0], P10[1]+5*down[1])): down = (-down[0], -down[1])
h11 = half_hpf(P10, (-down[0], -down[1]), c11, "halfhpf11"); pieces.append(h11)

mm, e, n = frame(5); F5 = (mm[0]+R*e[0]+R*n[0], mm[1]+R*e[1]+R*n[1]); mm, e, n = frame(11); F11 = (mm[0]+R*e[0]+R*n[0], mm[1]+R*e[1]+R*n[1])
existing = {"long crescent 5-6-7": D(F5) & ~D(C[6]) & ~D(C[7]), "long crescent 11-12-13": D(F11) & ~D(C[12]) & ~D(C[13])}
inpoly = np.zeros(xs.shape, bool)
for i in range(14):
    (x1, y1), (x2, y2) = Q[i], Q[(i+1) % 14]
    if y1 != y2: inpoly ^= ((y1 > ys) != (y2 > ys)) & (xs < x1 + (ys - y1) * (x2 - x1) / (y2 - y1))
worst = 0
for p in pieces:
    hits = {("circle %d" % j): (p["mask"] & D(C[j], R-0.2)).sum()*A_ for j in C}
    hits.update({nm: (p["mask"] & m).sum()*A_ for nm, m in existing.items()})
    hits.update({q["name"]: (p["mask"] & q["mask"]).sum()*A_ for q in pieces if q is not p})
    hits["outside the tile"] = (p["mask"] & ~inpoly).sum()*A_
    bad = {k: round(float(v), 1) for k, v in hits.items() if v > 0.5}; worst = max([worst] + list(bad.values()))
    print("%-9s %-8s area %.0f px^2, cusp (%.1f, %.1f), hand %s: %s" % (p["name"], p["kind"], p["mask"].sum()*A_, *p["cusp"], p["hand"], bad or "no overlap"))
print("5-8 gap: cusp of halfhpf08 is %.1f px from circle 5; its straight edge passes %.1f px from circle 5" % (dist(h8["cusp"], C[5]) - R,
      abs((C[5][0]-h8["cusp"][0])*(-h8["axis"][1]) + (C[5][1]-h8["cusp"][1])*h8["axis"][0]) - R))
print("touching checks: dome centre of halfhpf08 to circle 9 centre %.2f; halfhpf11 straight edge to A's centre %.2f; halfhpf11 dome centre to long-crescent circle %.2f (100 = just touching, 50 for the edge)"
      % (dist(h8["O"], C[9]), abs(a["O"][0]-P10[0]) if abs(h11["axis"][0]) < 1e-9 else -1, dist(h11["O"], F11)))
if write:
    assert worst <= 0.5, "refusing to draw overlapping pieces"
    NS = {"svg": "http://www.w3.org/2000/svg", "inkscape": "http://www.inkscape.org/namespaces/inkscape", "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"}
    for k, v in NS.items(): ET.register_namespace("" if k == "svg" else k, v)
    SVG, INK = "{%s}" % NS["svg"], "{%s}" % NS["inkscape"]
    tree = ET.parse("spectre.svg"); root = tree.getroot()
    el = {e_.get("id"): e_ for e_ in root.iter() if e_.get("id")}
    par = {c: p_ for p_ in root.iter() for c in p_}
    for old in ("cand_b", "centre_b"):
        if old in el: par[el[old]].remove(el[old])
    B = el["tileB"]; at = list(B).index(el["arc00out_b"])
    layer = ET.Element(SVG + "g", {INK + "groupmode": "layer", INK + "label": "Centre pieces", "id": "centre_b"}); B.insert(at, layer)
    defs = ET.SubElement(layer, SVG + "defs", {"id": "centre_defs_b"})
    W = 100/9
    for p in pieces:
        th = math.degrees(math.atan2(-p["axis"][0], p["axis"][1]))
        pat = ET.SubElement(defs, SVG + "pattern", {"id": p["name"] + "pat_b", "patternUnits": "userSpaceOnUse", "width": "%.5f" % (2*W), "height": "%.5f" % (2*W),
              "patternTransform": "translate(%.4f %.4f) rotate(%.4f) translate(%.5f 0)" % (*p["cusp"], th, -W/2)})
        ET.SubElement(pat, SVG + "rect", {"x": "0", "y": "0", "width": "%.5f" % W, "height": "%.5f" % (2*W), "style": "fill:%s;stroke:none" % p["col"]})
        ET.SubElement(layer, SVG + "path", {"id": p["name"] + "bg_b", "d": p["d"], "style": "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % p["col"]})
        ET.SubElement(layer, SVG + "path", {"id": p["name"] + "_b", "d": p["d"], "style": "fill:url(#%spat_b);stroke:none" % p["name"]})
    tree.write("spectre.svg", xml_declaration=True, encoding="UTF-8")
    print("wrote", [p["name"] for p in pieces])
