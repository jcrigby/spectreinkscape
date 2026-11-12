import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
C = {k+1: ((Q[k][0]+Q[(k+1)%14][0])/2, (Q[k][1]+Q[(k+1)%14][1])/2) for k in range(14)}
R, W, COL = 50.0, 100/9, "#8a3fc0"
dist = lambda a, b: math.hypot(a[0]-b[0], a[1]-b[1])
def meet(a, b, near):
    """Intersection of circles centred a and b (radius 50) closest to point `near`."""
    d = dist(a, b); mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
    hgt = math.sqrt(R*R - d*d/4); px, py = -(b[1]-a[1])/d, (b[0]-a[0])/d
    c1, c2 = (mx+hgt*px, my+hgt*py), (mx-hgt*px, my-hgt*py)
    return c1 if dist(c1, near) < dist(c2, near) else c2
toward = lambda a, b: (a[0] + R*(b[0]-a[0])/dist(a, b), a[1] + R*(b[1]-a[1])/dist(a, b))
c5, c6, c7, c8 = C[5], C[6], C[7], C[8]
ctr = tuple(sum(c[k] for c in (c5, c6, c7, c8))/4 for k in (0, 1))
V = [toward(c5, c8), meet(c5, c6, ctr), meet(c6, c7, ctr), meet(c7, c8, ctr), toward(c8, c5)]   # corners, in order
ARC_C = [c5, c6, c7, c8]                                                                      # centre of the arc leaving each corner
def arc(p, q, c):
    dx, dy = q[0]-p[0], q[1]-p[1]
    sweep = 1 if (c[0]-p[0])*(-dy) + (c[1]-p[1])*dx > 0 else 0
    for z in (p, q): assert abs(dist(z, c) - R) < 1e-6, (z, c)
    return "A 50 50 0 0 %d %.4f %.4f" % (sweep, *q)
def sample(p, q, c, n=24):
    a1, a2 = math.atan2(p[1]-c[1], p[0]-c[0]), math.atan2(q[1]-c[1], q[0]-c[0])
    da = (a2 - a1 + math.pi) % (2*math.pi) - math.pi
    return [(c[0]+R*math.cos(a1+da*t/n), c[1]+R*math.sin(a1+da*t/n)) for t in range(n)]
def clip(poly, nx, ny, lim, keep_below):
    out = []
    for k in range(len(poly)):
        a, b = poly[k], poly[(k+1) % len(poly)]
        fa, fb = a[0]*nx + a[1]*ny - lim, b[0]*nx + b[1]*ny - lim
        if not keep_below: fa, fb = -fa, -fb
        if fa <= 0: out.append(a)
        if (fa < 0 < fb) or (fb < 0 < fa):
            t = fa / (fa - fb); out.append((a[0] + t*(b[0]-a[0]), a[1] + t*(b[1]-a[1])))
    return out
def shoelace(p): return abs(sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p)))) / 2
def build(fwd):
    v = [fwd(p) for p in V]; cc = [fwd(c) for c in ARC_C]
    bg = "M %.4f %.4f " % v[0] + " ".join(arc(v[k], v[k+1], cc[k]) for k in range(4)) + " Z"
    outline = [pt for k in range(4) for pt in sample(v[k], v[k+1], cc[k])] + [v[4]]
    # stripes parallel to the piece's mirror axis (through the mid-points of 5-8 and 6-7), centred on it
    m1 = fwd(((c5[0]+c8[0])/2, (c5[1]+c8[1])/2)); m2 = fwd(((c6[0]+c7[0])/2, (c6[1]+c7[1])/2))
    L = dist(m1, m2); ax = ((m2[0]-m1[0])/L, (m2[1]-m1[1])/L); nx, ny = -ax[1], ax[0]
    off = m1[0]*nx + m1[1]*ny
    parts = []
    for k in range(-4, 5, 2):
        band = clip(clip(outline, nx, ny, off + (k+0.5)*W, True), nx, ny, off + (k-0.5)*W, False)
        if len(band) >= 3 and shoelace(band) > 0.5:
            parts.append("M " + " L ".join("%.3f %.3f" % p for p in band) + " Z")
    return bg, " ".join(parts), shoelace(outline)
def rigid(s0, s1, d0, d1):
    th = math.atan2(d1[1]-d0[1], d1[0]-d0[0]) - math.atan2(s1[1]-s0[1], s1[0]-s0[0]); c, s = math.cos(th), math.sin(th)
    return lambda p: (d0[0] + c*(p[0]-s0[0]) - s*(p[1]-s0[1]), d0[1] + s*(p[0]-s0[0]) + c*(p[1]-s0[1]))
PLACES = {"quad0234": rigid(c6, c7, C[2], C[3]), "quad5678": (lambda p: p), "quad1113": rigid(c5, c6, C[11], C[12])}
print("corner-to-corner side lengths:", ["%.1f" % dist(V[k], V[(k+1) % 5]) for k in range(5)])
def new(ident, d, style):
    ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
    ink.act("object-set-attribute", "d," + d)
    ink.act("object-set-attribute", "style," + style)
    ink.act("object-set-attribute", "id," + ident)
for name, fwd in PLACES.items():
    bg, stripes, a = build(fwd)
    print(name, "area %.0f" % a)
    if len(sys.argv) > 1 and sys.argv[1] == "draw":
        new(name + "bg", bg, "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % COL)
        new(name, stripes, "fill:%s;stroke:none" % COL)
        time.sleep(0.4)
if len(sys.argv) > 1 and sys.argv[1] == "draw":
    reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
    ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
    ink.act("select-clear"); ink.act("select-by-id", "layer-numbers"); ink.act("selection-top"); ink.act("select-clear")
