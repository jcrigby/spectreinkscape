import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
C = {k+1: ((Q[k][0]+Q[(k+1)%14][0])/2, (Q[k][1]+Q[(k+1)%14][1])/2) for k in range(14)}
R, W, COL = 50.0, 100/9, "#0a9396"
dist = lambda a, b: math.hypot(a[0]-b[0], a[1]-b[1])
def frame(k):                                     # circle number -> centre, edge direction, inward normal
    a, b = Q[k-1], Q[k % 14]; m = C[k]
    return m, ((b[0]-a[0])/100, (b[1]-a[1])/100), (-(a[1]-m[1])/R, (a[0]-m[0])/R)
def meets(a, b):
    d = dist(a, b); mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
    h = math.sqrt(R*R - d*d/4); px, py = -(b[1]-a[1])/d, (b[0]-a[0])/d
    return (mx+h*px, my+h*py), (mx-h*px, my-h*py)
def arc(p, q, c):
    dx, dy = q[0]-p[0], q[1]-p[1]
    sweep = 1 if (c[0]-p[0])*(-dy) + (c[1]-p[1])*dx > 0 else 0
    for z in (p, q): assert abs(dist(z, c) - R) < 1e-6, (z, c)
    return "A 50 50 0 0 %d %.4f %.4f" % (sweep, *q)
def sample(p, q, c, n=30):
    a1, a2 = math.atan2(p[1]-c[1], p[0]-c[0]), math.atan2(q[1]-c[1], q[0]-c[0])
    da = (a2 - a1 + math.pi) % (2*math.pi) - math.pi
    return [(c[0]+R*math.cos(a1+da*t/n), c[1]+R*math.sin(a1+da*t/n)) for t in range(n)]
def clip(poly, nx, ny, lim, below):
    out = []
    for k in range(len(poly)):
        a, b = poly[k], poly[(k+1) % len(poly)]
        fa, fb = a[0]*nx + a[1]*ny - lim, b[0]*nx + b[1]*ny - lim
        if not below: fa, fb = -fa, -fb
        if fa <= 0: out.append(a)
        if (fa < 0 < fb) or (fb < 0 < fa):
            t = fa / (fa - fb); out.append((a[0] + t*(b[0]-a[0]), a[1] + t*(b[1]-a[1])))
    return out
shoelace = lambda p: abs(sum(p[k][0]*p[(k+1) % len(p)][1] - p[(k+1) % len(p)][0]*p[k][1] for k in range(len(p)))) / 2

def long_crescent(k):
    """On circle k (fin toward k+1 at a 120-degree corner), with circle k+2 beyond a 90-degree corner."""
    m, e, n = frame(k); c1, c2 = C[k+1], C[k+2]
    XY = lambda u, v: (m[0]+u*e[0]+v*n[0], m[1]+u*e[1]+v*n[1])
    F, tip, Tk = XY(R, R), XY(R, 0), XY(0, R)        # fin-arc centre, sharp tip (polygon corner), corner of the 3qpf
    Y = XY(25, R*r3)                                  # where circle k meets circle k+1
    T2 = max(meets(c1, c2), key=lambda p: dist(p, tip) if dist(p, Q[(k+1) % 14]) > 1 else -1)   # k+1 meets k+2 inside the tile
    X = max(meets(F, c2), key=lambda p: dist(p, c1))  # extended fin circle meets circle k+2
    far = (F[0] + R*(F[0]-c1[0])/dist(F, c1), F[1] + R*(F[1]-c1[1])/dist(F, c1))                 # thickest point, opposite circle k+1
    seq = [(tip, Tk, F), (Tk, far, F), (far, X, F), (X, T2, c2), (T2, Y, c1), (Y, tip, c1)]
    d = "M %.4f %.4f " % tip + " ".join(arc(p, q, c) for p, q, c in seq) + " Z"
    outline = [pt for p, q, c in seq for pt in sample(p, q, c)]
    bands = []
    for j in range(0, 20, 2):                         # same stripe grid as circle k, carried on past its edge
        lo, hi = -R + j*W, -R + (j+1)*W
        off = m[0]*e[0] + m[1]*e[1]
        b = clip(clip(outline, e[0], e[1], off + hi, True), e[0], e[1], off + lo, False)
        if len(b) >= 3 and shoelace(b) > 0.3: bands.append("M " + " L ".join("%.3f %.3f" % p for p in b) + " Z")
    info = dict(tip=tip, corner_k=Tk, corner_k2=T2, X=X, area=shoelace(outline), thick=dist(F, c1),
                arc_on_k2=math.degrees(2*math.asin(dist(X, T2)/100)), fin_arc=math.degrees(2*math.asin(dist(tip, Tk)/100)))
    # sampled overlap check against every circle and the tile outline
    bad = 0; tot = 0
    for ix in range(0, 1300):
        for iy in range(0, 1000):
            x, y = 60 + ix*0.5, 40 + iy*0.5
            if abs(x-F[0]) > R or abs(y-F[1]) > R: continue
            if dist((x, y), F) < R and dist((x, y), c1) > R and dist((x, y), c2) > R:
                tot += 1
                if any(dist((x, y), C[j]) < R - 0.3 for j in C if j != k) or (dist((x, y), m) < R - 0.3 and not ((x-m[0])*e[0]+(y-m[1])*e[1] > 0 and (x-m[0])*n[0]+(y-m[1])*n[1] > 0)):
                    bad += 1
    info["overlap_samples"] = (bad, tot)
    return d, " ".join(bands), info

if __name__ == "__main__":
    k = int(sys.argv[1]); d, stripes, info = long_crescent(k)
    for a, b in info.items(): print(a, b if not isinstance(b, tuple) or len(b) != 2 or a == "overlap_samples" else "(%.1f, %.1f)" % b)
    if len(sys.argv) > 2 and sys.argv[2] == "draw":
        sfx = "_b"
        def new(ident, dd, style):
            ink.act("select-clear"); ink.act("select-by-id", "spectre" + sfx); ink.act("duplicate")
            ink.act("object-set-attribute", "d," + dd)
            ink.act("object-set-attribute", "style," + style)
            ink.act("object-set-attribute", "id," + ident + sfx)
        old = sys.argv[3]
        ink.act("select-clear"); ink.act("select-by-id", ",".join(x + sfx for x in old.split(","))); ink.act("delete-selection")
        new("longcres%02dbg" % k, d, "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % COL)
        new("longcres%02d" % k, stripes, "fill:%s;stroke:none" % COL)
        reds = ",".join("arc%02d%s%s" % (i, "out" if i % 2 == 0 else "in", sfx) for i in range(14))
        ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
        ink.act("select-clear"); ink.act("select-by-id", "layer-numbers" + sfx); ink.act("selection-top"); ink.act("select-clear")
