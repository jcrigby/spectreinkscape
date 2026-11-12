import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
R, N, GREEN = 50.0, 9, "#1a9a3a"
def arc(p, q, c):
    dx, dy = q[0]-p[0], q[1]-p[1]
    sweep = 1 if (c[0]-p[0])*(-dy) + (c[1]-p[1])*dx > 0 else 0
    for z in (p, q): assert abs(math.hypot(z[0]-c[0], z[1]-c[1]) - R) < 1e-6, (z, c)
    return "A 50 50 0 0 %d %.4f %.4f" % (sweep, *q)
f = lambda p: "%.4f %.4f" % p
FIN_SIDE = {0: -1, 4: 1, 8: 1, 10: 1, 12: -1}      # circle index -> which end its fin is on
OLD = {0: "tile00,quart01,fin01", 4: "tile04,quart05,fin05e", 8: "tile08,quart09,fin09e",
       10: "tile10,quart11,fin11e", 12: "tile12,quart13,fin13"}
def new(ident, d, style):
    ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
    ink.act("object-set-attribute", "d," + d)
    ink.act("object-set-attribute", "style," + style)
    ink.act("object-set-attribute", "id," + ident)
for i, s in FIN_SIDE.items():
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    e = ((b[0]-a[0])/100, (b[1]-a[1])/100); n = (-(a[1]-m[1])/R, (a[0]-m[0])/R)
    XY = lambda u, v: (m[0]+u*e[0]+v*n[0], m[1]+u*e[1]+v*n[1])
    F = XY(s*R, R)
    h = lambda u: math.sqrt(max(R*R-u*u, 0))
    top = lambda u: (R - math.sqrt(max(R*R-(R-s*u)**2, 0))) if s*u > 0 else h(u)
    tip, bot, far, up = XY(s*R, 0), XY(0, -R), XY(-s*R, 0), XY(0, R)
    bg = "M %s %s %s %s %s Z" % (f(tip), arc(tip, bot, m), arc(bot, far, m), arc(far, up, m), arc(up, tip, F))
    parts = []
    for k in range(0, N, 2):
        u1, u2 = -R + k*2*R/N, -R + (k+1)*2*R/N
        p1, p2 = XY(u1, -h(u1)), XY(u2, -h(u2))
        d = "M %s %s" % (f(p1), arc(p1, p2, m))
        cuts = [u2, 0.0, u1] if u1 < 0 < u2 else [u2, u1]
        prev = None
        for u in cuts:
            q = XY(u, top(u))
            if prev is None: d += " L %s" % f(q)
            else:
                mid = (prev[0] + u) / 2
                d += " " + arc(prev[1], q, F if s*mid > 0 else m)
            prev = (u, q)
        parts.append(d + " Z")
    old = ",".join(x + "," + x + "bg" for x in OLD[i].split(","))
    ink.act("select-clear"); ink.act("select-by-id", old); ink.act("delete-selection")
    new("p3qpf%02dbg" % (i+1), bg, "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % GREEN)
    new("p3qpf%02d" % (i+1), " ".join(parts), "fill:%s;stroke:none" % GREEN)
    time.sleep(0.4)
reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
ink.act("select-clear"); ink.act("select-by-id", "layer-numbers"); ink.act("selection-top"); ink.act("select-clear")
