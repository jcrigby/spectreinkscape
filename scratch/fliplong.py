import math, sys, importlib.util
draw = len(sys.argv) > 1 and sys.argv[1] == "draw"; sys.argv = sys.argv[:1]
spec = importlib.util.spec_from_file_location("l3", __file__.replace("fliplong.py", "longcres3.py")); l3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(l3)
lc = l3.lc; C, R, W, COL, dist, arc, sample, clip, shoelace, ink = lc.C, lc.R, lc.W, lc.COL, lc.dist, lc.arc, lc.sample, lc.clip, lc.shoelace, lc.ink
F, c4, m3 = l3.seq[0][2], l3.seq[5][2], C[3]
ax = ((F[0]-c4[0])/dist(F, c4), (F[1]-c4[1])/dist(F, c4))
def mir(p):                                           # mirror across the crescent's own axis (through F and circle 4's centre)
    w = (p[0]-c4[0], p[1]-c4[1]); al = w[0]*ax[0]+w[1]*ax[1]
    return (c4[0]+2*al*ax[0]-w[0], c4[1]+2*al*ax[1]-w[1])
seq = [(mir(p), mir(q), mir(c)) for p, q, c in l3.seq]
d = "M %.4f %.4f " % seq[0][0] + " ".join(arc(p, q, c) for p, q, c in seq) + " Z"
outline = [pt for p, q, c in seq for pt in sample(p, q, c, 40)]
ed, md = l3.ed, l3.md; off = md[0]*ed[0] + md[1]*ed[1]
bands = []
for j in range(0, 20, 2):
    b = clip(clip(l3.outline, ed[0], ed[1], off - R + (j+1)*W, True), ed[0], ed[1], off - R + j*W, False)
    if len(b) >= 3 and shoelace(b) > 0.3: bands.append("M " + " L ".join("%.3f %.3f" % mir(p) for p in b) + " Z")
ov = outline                                          # overlap = piece clipped to circle 3 (as a 120-gon)
for t in range(120):
    a = 2*math.pi*t/120; nx, ny = math.cos(a), math.sin(a)
    ov = clip(ov, nx, ny, m3[0]*nx + m3[1]*ny + R*math.cos(math.pi/120), True)
    if len(ov) < 3: break
print("flipped piece %.0f px^2; overlap with circle 3's pieces %.0f px^2; sharp tip at (%.1f, %.1f)" % (shoelace(outline), shoelace(ov) if len(ov) >= 3 else 0, *seq[0][0]))
if draw:
    sfx = "_b"
    def new(ident, dd, style):
        ink.act("select-clear"); ink.act("select-by-id", "spectre" + sfx); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + dd); ink.act("object-set-attribute", "style," + style); ink.act("object-set-attribute", "id," + ident + sfx)
    new("fliplong03bg", d, "fill:#ffffff;fill-opacity:0.6;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % COL)
    new("fliplong03", " ".join(bands), "fill:%s;fill-opacity:0.8;stroke:none" % COL)
    new("overlap03", "M " + " L ".join("%.3f %.3f" % p for p in ov) + " Z", "fill:#d0006f;stroke:#7a0040;stroke-width:0.8;stroke-linejoin:round")
    reds = ",".join("arc%02d%s%s" % (i, "out" if i % 2 == 0 else "in", sfx) for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
    ink.act("select-clear"); ink.act("select-by-id", "layer-numbers" + sfx); ink.act("selection-top"); ink.act("select-clear")
