import math, sys, time
sys.path.insert(0, ".claude/skills/inkscape-live")
import ink
r3 = math.sqrt(3)/2
P = [(0,0),(1,0),(1.5,-r3),(1.5+r3,.5-r3),(1.5+r3,1.5-r3),(2.5+r3,1.5-r3),(3+r3,1.5),
     (3,2),(3-r3,1.5),(2.5-r3,1.5+r3),(1.5-r3,1.5+r3),(.5-r3,1.5+r3),(-r3,1.5),(0,1)]
Q = [(200+100*x, 350-100*y) for x, y in P]
R, N, BLUE = 50.0, 9, "#2060d0"
def new(ident, d, style):
    ink.act("select-clear"); ink.act("select-by-id", "spectre"); ink.act("duplicate")
    ink.act("object-set-attribute", "d," + d)
    ink.act("object-set-attribute", "style," + style)
    ink.act("object-set-attribute", "id," + ident)
for i in (0, 12):                                   # circles 1 and 13: leftover is the start quarter
    a, b = Q[i], Q[(i+1) % 14]
    m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    e = ((b[0]-a[0])/100, (b[1]-a[1])/100)
    n = (-(a[1]-m[1])/R, (a[0]-m[0])/R)
    XY = lambda u, v: (m[0]+u*e[0]+v*n[0], m[1]+u*e[1]+v*n[1])
    pt = lambda u, v: "%.4f %.4f" % XY(u, v)
    # the neighbouring circle is centred on the far corner of the 50x50 square
    pm = Q[i-1]; nb = ((pm[0]+a[0])/2, (pm[1]+a[1])/2); far = XY(-R, R)
    assert math.hypot(nb[0]-far[0], nb[1]-far[1]) < 1e-6, (nb, far)
    g = lambda u: R - math.sqrt(max(R*R - (u+R)**2, 0))      # height under the neighbour's arc
    new("spand%02dbg" % (i+1), "M %s L %s A 50 50 0 0 0 %s Z" % (pt(0, 0), pt(-R, 0), pt(0, R)),
        "fill:#ffffff;stroke:%s;stroke-width:1.5;stroke-linejoin:round" % BLUE)
    bands = []
    for k in range(0, N, 2):
        u1, u2 = -R + k*2*R/N, min(-R + (k+1)*2*R/N, 0.0)
        if u2 <= u1: continue
        bands.append("M %s L %s L %s A 50 50 0 0 1 %s Z" % (pt(u1, 0), pt(u2, 0), pt(u2, g(u2)), pt(u1, g(u1))))
    new("spand%02d" % (i+1), " ".join(bands), "fill:%s;stroke:none" % BLUE)
    time.sleep(0.3)
reds = ",".join("arc%02d%s" % (i, "out" if i % 2 == 0 else "in") for i in range(14))
ink.act("select-clear"); ink.act("select-by-id", reds); ink.act("selection-top")
ink.act("select-clear"); ink.act("select-by-id", "layer-numbers"); ink.act("selection-top"); ink.act("select-clear")
