import math, sys, importlib.util
deg = float(sys.argv[1]); draw = len(sys.argv) > 2 and sys.argv[2] == "draw"; sys.argv = sys.argv[:1]
spec = importlib.util.spec_from_file_location("fl", __file__.replace("fliplong_slide.py", "fliplong.py")); fl = importlib.util.module_from_spec(spec); spec.loader.exec_module(fl)
lc = fl.lc; arc, sample, clip, shoelace, ink, COL, R, W, dist = lc.arc, lc.sample, lc.clip, lc.shoelace, lc.ink, lc.COL, lc.R, lc.W, lc.dist
c4 = fl.c4
def rot(p):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a); x, y = p[0]-c4[0], p[1]-c4[1]
    return (c4[0]+c*x-s*y, c4[1]+s*x+c*y)
seq = [(rot(p), rot(q), rot(c)) for p, q, c in fl.seq]
d = "M %.4f %.4f " % seq[0][0] + " ".join(arc(p, q, c) for p, q, c in seq) + " Z"
l3 = fl.l3; ed, md = l3.ed, l3.md; off = md[0]*ed[0] + md[1]*ed[1]
bands = []
for j in range(0, 20, 2):
    b = clip(clip(l3.outline, ed[0], ed[1], off - R + (j+1)*W, True), ed[0], ed[1], off - R + j*W, False)
    if len(b) >= 3 and shoelace(b) > 0.3: bands.append("M " + " L ".join("%.3f %.3f" % rot(fl.mir(p)) for p in b) + " Z")
print("sharp tip at (%.1f, %.1f); tile corner between 4 and 5 is (%.1f, %.1f)" % (*seq[0][0], *lc.Q[4]))
if draw:
    sfx = "_b"
    def new(ident, dd, style):
        ink.act("select-clear"); ink.act("select-by-id", "spectre" + sfx); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + dd); ink.act("object-set-attribute", "style," + style); ink.act("object-set-attribute", "id," + ident + sfx)
    ink.act("select-clear"); ink.act("select-by-id", "fliplong04_b,fliplong04bg_b"); ink.act("delete-selection")
    new("fliplong04bg", d, "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % COL)
    new("fliplong04", " ".join(bands), "fill:%s;stroke:none" % COL)
    reds = ",".join("arc%02d%s%s" % (i, "out" if i % 2 == 0 else "in", sfx) for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
    ink.act("select-clear"); ink.act("select-by-id", "layer-numbers" + sfx); ink.act("selection-top"); ink.act("select-clear")
