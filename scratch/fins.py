import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
R, N, BLUE = 50.0, 9, "#2060d0"
def frame(i):
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    return m, ((b[0]-a[0])/100, (b[1]-a[1])/100), (-(a[1]-m[1])/R, (a[0]-m[0])/R)
C = [frame(i)[0] for i in range(14)]
# (circle index, side): side -1 = quarter at the start corner, +1 = quarter at the end corner
WANT = [(2, -1), (2, 1), (4, 1), (6, -1), (6, 1), (8, 1), (10, 1)]
g = lambda w: R - math.sqrt(max(R*R - (R-w)**2, 0))   # fin height at distance w from the centre along the diameter

ok = []
for i, side in WANT:
    m, e, n = frame(i); tot = bad = 0; deepest = 0.0; gap = 0
    for sw in range(1, 100):
        for sv in range(1, 100):
            w, v = sw/2, sv/2
            if w*w + v*v >= R*R: continue                       # stay in own quarter
            x, y = m[0]+side*w*e[0]+v*n[0], m[1]+side*w*e[1]+v*n[1]
            others = [R - math.hypot(x-C[j][0], y-C[j][1]) for j in range(14) if j != i]
            infin = v < g(w)
            if infin:
                tot += 1
                if max(others) > 1e-6: bad += 1; deepest = max(deepest, max(others))
            elif max(others) <= 0: gap += 1                      # neither fin nor another circle
    print("circle %2d %s: fin overlap %d of %d samples (deepest %.2fpx), uncovered gap %.0f px^2"
          % (i+1, "start" if side < 0 else "end  ", bad, tot, deepest, gap/4))
    if bad == 0: ok.append((i, side))

if len(sys.argv) > 1 and sys.argv[1] == "draw":
    def new(ident, d, style):
        ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
        ink.act("object-set-attribute", "d," + d)
        ink.act("object-set-attribute", "style," + style)
        ink.act("object-set-attribute", "id," + ident)
    for i, side in ok:
        m, e, n = frame(i)
        pt = lambda w, v: "%.4f %.4f" % (m[0]+side*w*e[0]+v*n[0], m[1]+side*w*e[1]+v*n[1])
        sw = 0 if side < 0 else 1
        name = "fin%02d%s" % (i+1, "s" if side < 0 else "e")
        new(name + "bg", "M %s L %s A 50 50 0 0 %d %s Z" % (pt(0, 0), pt(R, 0), sw, pt(0, R)),
            "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % BLUE)
        bands = []
        for k in range(0, N, 2):                                # same band grid as the tile's stripes
            u1, u2 = -R + k*2*R/N, -R + (k+1)*2*R/N
            lo, hi = (max(u1, 0), min(u2, R)) if side > 0 else (max(-u2, 0), min(-u1, R))
            if hi <= lo: continue
            bands.append("M %s L %s L %s A 50 50 0 0 %d %s Z" % (pt(lo, 0), pt(hi, 0), pt(hi, g(hi)), 1 - sw, pt(lo, g(lo))))
        new(name, " ".join(bands), "fill:%s;stroke:none" % BLUE)
        time.sleep(0.3)
    for i in (2, 6):                                            # halves now hold two fins: park the number in the corner shared with the previous circle
        m, e, n = frame(i)
        ink.act("select-clear"); ink.act("select-by-id", "num%02d" % (i+1))
        ink.act("object-set-attribute", "x,%.2f" % (m[0]-24*e[0]+24*n[0])); ink.act("object-set-attribute", "y,%.2f" % (m[1]-24*e[1]+24*n[1]+7))
    reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
    ink.act("select-clear"); ink.act("select-by-id", "layer-numbers"); ink.act("selection-top"); ink.act("select-clear")
