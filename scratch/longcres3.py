import math, sys, importlib.util
spec = importlib.util.spec_from_file_location("lc", __file__.replace("longcres3.py", "longcres.py")); lc = importlib.util.module_from_spec(spec); spec.loader.exec_module(lc)
C, R, W, COL, dist, frame, meets, arc, sample, clip, shoelace, ink = lc.C, lc.R, lc.W, lc.COL, lc.dist, lc.frame, lc.meets, lc.arc, lc.sample, lc.clip, lc.shoelace, lc.ink
SRC, DST = 11, 3                                   # build the piece where it is defined, then move it rigidly
ms, es, ns = frame(SRC); md, ed, nd = frame(DST)
def move(p):
    u, v = (p[0]-ms[0])*es[0] + (p[1]-ms[1])*es[1], (p[0]-ms[0])*ns[0] + (p[1]-ms[1])*ns[1]
    return (md[0]+u*ed[0]+v*nd[0], md[1]+u*ed[1]+v*nd[1])
XY = lambda u, v: (ms[0]+u*es[0]+v*ns[0], ms[1]+u*es[1]+v*ns[1])
c1, c2 = C[SRC+1], C[SRC+2]
F, tip, Tk, Y = XY(R, R), XY(R, 0), XY(0, R), XY(25, R*math.sqrt(3)/2)
T2 = max(meets(c1, c2), key=lambda p: dist(p, tip) if dist(p, lc.Q[(SRC+1) % 14]) > 1 else -1)
X = max(meets(F, c2), key=lambda p: dist(p, c1))
far = (F[0] + R*(F[0]-c1[0])/dist(F, c1), F[1] + R*(F[1]-c1[1])/dist(F, c1))
seq = [tuple(move(z) for z in t) for t in [(tip, Tk, F), (Tk, far, F), (far, X, F), (X, T2, c2), (T2, Y, c1), (Y, tip, c1)]]
assert dist(seq[5][2], C[DST+1]) < 1e-6 and dist(seq[0][0], lc.Q[DST % 14]) < 1e-6        # hugs circle 4, tip on the 3/4 corner
d = "M %.4f %.4f " % seq[0][0] + " ".join(arc(p, q, c) for p, q, c in seq) + " Z"
outline = [pt for p, q, c in seq for pt in sample(p, q, c)]
bands = []
off = md[0]*ed[0] + md[1]*ed[1]
for j in range(0, 20, 2):
    b = clip(clip(outline, ed[0], ed[1], off - R + (j+1)*W, True), ed[0], ed[1], off - R + j*W, False)
    if len(b) >= 3 and shoelace(b) > 0.3: bands.append("M " + " L ".join("%.3f %.3f" % p for p in b) + " Z")
vc = move(c2)
print("piece area %.0f; blunt end faces a spot centred (%.1f, %.1f); clearance of that spot's circle from real circles: %s"
      % (shoelace(outline), *vc, {j: round(dist(vc, C[j]) - 100, 1) for j in C if dist(vc, C[j]) < 140}))
# overlap check for the moved piece
Fd, c1d = move(F), move(c1); bad = tot = 0
for ix in range(400):
    for iy in range(400):
        x, y = Fd[0]-50+ix*0.25, Fd[1]-50+iy*0.25
        if dist((x, y), Fd) < R and dist((x, y), c1d) > R and dist((x, y), vc) > R:
            tot += 1
            for j in C:
                if j == DST:
                    u, v = (x-md[0])*ed[0]+(y-md[1])*ed[1], (x-md[0])*nd[0]+(y-md[1])*nd[1]
                    if dist((x, y), md) < R - 0.3 and not (u > 0 and v > 0): bad += 1
                elif j != DST+1 and dist((x, y), C[j]) < R - 0.3: bad += 1
print("overlapping samples: %d of %d (area %.0f)" % (bad, tot, tot/16))
if len(sys.argv) > 1 and sys.argv[1] == "draw":
    sfx = "_b"
    def new(ident, dd, style):
        ink.act("select-clear"); ink.act("select-by-id", "spectre" + sfx); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + dd); ink.act("object-set-attribute", "style," + style); ink.act("object-set-attribute", "id," + ident + sfx)
    ink.act("select-clear"); ink.act("select-by-id", ",".join(x + sfx for x in ("cres03", "cres03bg", "star0234", "star0234bg"))); ink.act("delete-selection")
    new("longcres03bg", d, "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % COL)
    new("longcres03", " ".join(bands), "fill:%s;stroke:none" % COL)
    reds = ",".join("arc%02d%s%s" % (i, "out" if i % 2 == 0 else "in", sfx) for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
    ink.act("select-clear"); ink.act("select-by-id", "layer-numbers" + sfx); ink.act("selection-top"); ink.act("select-clear")
